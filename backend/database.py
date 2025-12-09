# backend/database.py
from pymongo import MongoClient
from config import Config

class MongoDatabase:
    """MongoDB connection manager"""
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        """Create MongoDB connection"""
        if cls._client is None:
            cls._client = MongoClient(Config.MONGODB_URI)
            cls._db = cls._client[Config.MONGODB_DB_NAME]
            # Create indexes
            cls._create_indexes()
        return cls._db

    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls._db is None:
            cls.connect()
        return cls._db

    @classmethod
    def close(cls):
        """Close database connection"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None

    @classmethod
    def _create_indexes(cls):
        """Create database indexes for performance"""
        try:
            db = cls._db
            # User indexes
            try:
                db.users.create_index("email", unique=True)
                db.users.create_index("created_at")
            except Exception as e:
                print(f"Warning: Could not create user indexes: {e}")
            
            # Itinerary indexes
            try:
                db.itineraries.create_index("user_id")
                db.itineraries.create_index("destination")
                db.itineraries.create_index("created_at")
                db.itineraries.create_index([("user_id", 1), ("created_at", -1)])
            except Exception as e:
                print(f"Warning: Could not create itinerary indexes: {e}")
        except Exception as e:
            print(f"Warning: Index creation failed: {e}")

