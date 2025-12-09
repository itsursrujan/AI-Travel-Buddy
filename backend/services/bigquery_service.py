# backend/services/bigquery_service.py
try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError as e:
    print("[WARNING] BigQuery import warning: " + str(e))
    BIGQUERY_AVAILABLE = False

import os
from datetime import datetime
import json
import uuid

class BigQueryService:
    def __init__(self):
        """Initialize BigQuery client"""
        if not BIGQUERY_AVAILABLE:
            print("[INFO] BigQuery not available - install google-cloud-bigquery")
            self.client = None
            return
            
        try:
            # Use environment variable or look for credentials file
            credentials_path = os.getenv('GOOGLE_CLOUD_CREDENTIALS_PATH')
            if not credentials_path:
                # Try multiple possible locations
                possible_paths = [
                    'keen-enigma-480714-m1-534f32663c78.json',
                    '../backend/keen-enigma-480714-m1-534f32663c78.json',
                    'c:\\Users\\Srujan Aravalli\\Desktop\\AI Travel Buddy\\backend\\keen-enigma-480714-m1-534f32663c78.json'
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        credentials_path = path
                        break
            
            self.project_id = os.getenv('GCP_PROJECT_ID', 'keen-enigma-480714-m1')
            self.dataset_id = os.getenv('BQ_DATASET_ID', 'travel_buddy')
            
            # Check if credentials file exists
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.client = bigquery.Client(credentials=credentials, project=self.project_id)
                print("[OK] BigQuery connected with service account credentials")
            else:
                # Fall back to Application Default Credentials
                self.client = bigquery.Client(project=self.project_id)
                print("[OK] BigQuery connected using Application Default Credentials")
            
            print("[OK] Project ID: " + self.project_id)
            print("[OK] Dataset ID: " + self.dataset_id)
            
        except Exception as e:
            print("[ERROR] Error initializing BigQuery: " + str(e))
            self.client = None

    def create_tables(self):
        """Create necessary BigQuery tables if they don't exist"""
        if not self.client:
            print("✗ BigQuery client not initialized")
            return False
        
        try:
            dataset_id = f"{self.project_id}.{self.dataset_id}"
            
            # Create dataset if it doesn't exist
            try:
                self.client.get_dataset(dataset_id)
                print(f"✓ Dataset {self.dataset_id} already exists")
            except Exception:
                from google.cloud.bigquery import Dataset
                dataset = Dataset(dataset_id)
                dataset.location = "US"
                self.client.create_dataset(dataset, exists_ok=True)
                print(f"✓ Created dataset {self.dataset_id}")
            
            # Users table
            users_schema = [
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            
            # Itineraries table
            itineraries_schema = [
                bigquery.SchemaField("itinerary_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("destination", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("budget", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("days", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("travel_style", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("total_cost", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            
            # Attractions table
            attractions_schema = [
                bigquery.SchemaField("attraction_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("itinerary_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("day", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("latitude", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("longitude", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("rating", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("image_url", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            
            # User Analytics table
            analytics_schema = [
                bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("destination", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ]
            
            tables = [
                ("users", users_schema),
                ("itineraries", itineraries_schema),
                ("attractions", attractions_schema),
                ("user_analytics", analytics_schema),
            ]
            
            for table_name, schema in tables:
                table_id = f"{dataset_id}.{table_name}"
                
                if not self._table_exists(table_id):
                    table = bigquery.Table(table_id, schema=schema)
                    self.client.create_table(table)
                    print(f"✓ Created table {table_name}")
                else:
                    print(f"✓ Table {table_name} already exists")
            
            return True
        except Exception as e:
            print(f"✗ Error creating tables: {str(e)}")
            return False

    def _table_exists(self, table_id):
        """Check if a table exists"""
        try:
            self.client.get_table(table_id)
            return True
        except Exception:
            return False

    def log_user(self, user_id, email):
        """Log user data to BigQuery"""
        if not self.client:
            return False
        
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.users"
            rows_to_insert = [
                {
                    "user_id": user_id,
                    "email": email,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                }
            ]
            
            errors = self.client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                print(f"✗ Errors inserting user data: {errors}")
                return False
            print(f"✓ Logged user: {email}")
            return True
        except Exception as e:
            print(f"✗ Error logging user: {str(e)}")
            return False

    def log_itinerary(self, itinerary_id, user_id, destination, budget, days, travel_style, total_cost):
        """Log itinerary creation to BigQuery"""
        if not self.client:
            return False
        
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.itineraries"
            rows_to_insert = [
                {
                    "itinerary_id": itinerary_id,
                    "user_id": user_id,
                    "destination": destination,
                    "budget": float(budget),
                    "days": int(days),
                    "travel_style": travel_style,
                    "total_cost": float(total_cost),
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                }
            ]
            
            errors = self.client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                print(f"✗ Errors inserting itinerary data: {errors}")
                return False
            print(f"✓ Logged itinerary: {destination} ({days} days)")
            return True
        except Exception as e:
            print(f"✗ Error logging itinerary: {str(e)}")
            return False

    def log_attraction(self, attraction_id, itinerary_id, name, description, day, latitude, longitude, rating, image_url):
        """Log attraction to BigQuery"""
        if not self.client:
            return False
        
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.attractions"
            rows_to_insert = [
                {
                    "attraction_id": attraction_id,
                    "itinerary_id": itinerary_id,
                    "name": name,
                    "description": description,
                    "day": int(day),
                    "latitude": float(latitude) if latitude else None,
                    "longitude": float(longitude) if longitude else None,
                    "rating": float(rating) if rating else None,
                    "image_url": image_url,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                }
            ]
            
            errors = self.client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                print(f"✗ Errors inserting attraction data: {errors}")
                return False
            print(f"✓ Logged attraction: {name}")
            return True
        except Exception as e:
            print(f"✗ Error logging attraction: {str(e)}")
            return False

    def log_event(self, user_id, event_type, destination=None, metadata=None):
        """Log user events for analytics"""
        if not self.client:
            return False
        
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.user_analytics"
            rows_to_insert = [
                {
                    "event_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "event_type": event_type,
                    "destination": destination,
                    "metadata": json.dumps(metadata) if metadata else None,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                }
            ]
            
            errors = self.client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                print(f"✗ Errors inserting event data: {errors}")
                return False
            print(f"✓ Logged event: {event_type}")
            return True
        except Exception as e:
            print(f"✗ Error logging event: {str(e)}")
            return False

    def get_popular_destinations(self, limit=10):
        """Get most popular travel destinations"""
        if not self.client:
            return []
        
        try:
            query = f"""
            SELECT destination, COUNT(*) as count
            FROM `{self.project_id}.{self.dataset_id}.itineraries`
            GROUP BY destination
            ORDER BY count DESC
            LIMIT {limit}
            """
            
            results = self.client.query(query).result()
            data = [dict(row) for row in results]
            print(f"✓ Fetched {len(data)} popular destinations")
            return data
        except Exception as e:
            print(f"✗ Error fetching popular destinations: {str(e)}")
            return []

    def get_travel_style_stats(self):
        """Get statistics about travel styles"""
        if not self.client:
            return {}
        
        try:
            query = f"""
            SELECT travel_style, COUNT(*) as count, AVG(budget) as avg_budget, AVG(total_cost) as avg_cost
            FROM `{self.project_id}.{self.dataset_id}.itineraries`
            GROUP BY travel_style
            """
            
            results = self.client.query(query).result()
            data = {}
            for row in results:
                data[row.travel_style] = {
                    "count": row.count,
                    "avg_budget": float(row.avg_budget) if row.avg_budget else 0,
                    "avg_cost": float(row.avg_cost) if row.avg_cost else 0
                }
            print(f"✓ Fetched travel style stats for {len(data)} styles")
            return data
        except Exception as e:
            print(f"✗ Error fetching travel style stats: {str(e)}")
            return {}

    def get_user_insights(self, user_id):
        """Get analytics insights for a specific user"""
        if not self.client:
            return {}
        
        try:
            query = f"""
            SELECT 
                COUNT(DISTINCT itinerary_id) as total_itineraries,
                COUNT(DISTINCT destination) as unique_destinations,
                AVG(budget) as avg_budget,
                SUM(total_cost) as total_spent,
                MAX(created_at) as last_itinerary
            FROM `{self.project_id}.{self.dataset_id}.itineraries`
            WHERE user_id = '{user_id}'
            """
            
            results = self.client.query(query).result()
            if results.total_rows > 0:
                row = next(results)
                data = {
                    "total_itineraries": row.total_itineraries,
                    "unique_destinations": row.unique_destinations,
                    "avg_budget": float(row.avg_budget) if row.avg_budget else 0,
                    "total_spent": float(row.total_spent) if row.total_spent else 0,
                    "last_itinerary": row.last_itinerary.isoformat() if row.last_itinerary else None
                }
                print(f"✓ Fetched user insights for {user_id}")
                return data
            return {}
        except Exception as e:
            print(f"✗ Error fetching user insights: {str(e)}")
            return {}

    def get_top_attractions(self, limit=10):
        """Get most viewed attractions across all itineraries"""
        if not self.client:
            return []
        
        try:
            query = f"""
            SELECT name, COUNT(*) as appearances, AVG(CAST(rating AS FLOAT64)) as avg_rating
            FROM `{self.project_id}.{self.dataset_id}.attractions`
            GROUP BY name
            ORDER BY appearances DESC
            LIMIT {limit}
            """
            
            results = self.client.query(query).result()
            data = []
            for row in results:
                data.append({
                    "name": row.name,
                    "appearances": row.appearances,
                    "avg_rating": float(row.avg_rating) if row.avg_rating else 0
                })
            print(f"✓ Fetched {len(data)} top attractions")
            return data
        except Exception as e:
            print(f"✗ Error fetching top attractions: {str(e)}")
            return []
