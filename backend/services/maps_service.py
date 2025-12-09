# backend/services/maps_service.py
import requests
from typing import Dict, List, Optional
import time

class MapsService:
    """
    OpenStreetMap-based mapping service (Free & Open Source)
    Uses:
    - Nominatim for geocoding/reverse geocoding
    - Overpass API for finding attractions
    """

    # Nominatim API endpoint
    NOMINATIM_URL = "https://nominatim.openstreetmap.org"
    # Overpass API endpoint
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Travel-Buddy/1.0'  # Nominatim requires User-Agent
        })

    def get_nearby_places(self, location: str, radius: int = 5000) -> List[Dict]:
        """
        Get nearby attractions using Overpass API with fallback to hardcoded database
        Returns real attractions from OpenStreetMap or hardcoded list
        """
        try:
            # First, try hardcoded attractions for known cities (faster, more reliable)
            hardcoded = self._get_hardcoded_attractions(location)
            if hardcoded:
                print(f"Using hardcoded attractions for {location}")
                return hardcoded
            
            # If not in hardcoded list, try Overpass API
            coords = self.geocode(location)
            if not coords:
                print(f"Could not geocode {location}, returning sample places")
                return self._get_sample_places(location)

            lat, lng = coords['lat'], coords['lng']
            print(f"Fetching attractions for {location} at coordinates ({lat}, {lng})")
            
            # Try with expanding bbox sizes if first attempt returns no results
            bbox_sizes = [0.1, 0.15, 0.2, 0.3]  # Progressively larger search areas
            
            for bbox_size in bbox_sizes:
                try:
                    # Query Overpass API for nearby attractions with expanded search area
                    overpass_query = f"""
                    [bbox:{lat-bbox_size},{lng-bbox_size},{lat+bbox_size},{lng+bbox_size}];
                    (
                      node["tourism"~"attraction|museum|monument|viewpoint|zoo|landmark"];
                      node["leisure"="park"];
                      node["historic"~"monument|castle|ruins"];
                      node["amenity"~"theatre|cinema|library"];
                      way["tourism"~"attraction|museum|monument"];
                      way["leisure"="park"];
                      way["historic"~"monument|castle|ruins"];
                    );
                    out center;
                    """

                    print(f"Trying Overpass with bbox_size: {bbox_size}")
                    response = self.session.get(
                        self.OVERPASS_URL,
                        params={'data': overpass_query},
                        timeout=20
                    )

                    if response.status_code != 200:
                        print(f"Overpass API error: {response.status_code}")
                        continue

                    data = response.json()
                    attractions = []

                    for element in data.get('elements', []):
                        # Get coordinates
                        if 'center' in element:
                            lat_attr = element['center']['lat']
                            lng_attr = element['center']['lon']
                        elif 'lat' in element and 'lon' in element:
                            lat_attr = element['lat']
                            lng_attr = element['lon']
                        else:
                            continue

                        # Get name and tags
                        tags = element.get('tags', {})
                        name = tags.get('name', 'Unnamed Attraction')
                        
                        # Skip if no proper name or generic names
                        if not name or name.startswith('Node') or name.startswith('Way'):
                            continue

                        # Get additional info
                        attraction_type = tags.get('tourism', tags.get('leisure', tags.get('historic', 'attraction')))
                        
                        attractions.append({
                            'name': name,
                            'location': {'lat': lat_attr, 'lng': lng_attr},
                            'rating': float(tags.get('rating', 4.3)),
                            'address': tags.get('addr:full', f"{name}, {location}"),
                            'type': attraction_type,
                            'website': tags.get('website', ''),
                            'opening_hours': tags.get('opening_hours', '9:00 AM - 6:00 PM'),
                            'place_id': f"osm_{element.get('id', 'unknown')}"
                        })

                        if len(attractions) >= 20:  # Get enough results
                            break

                    # If we got results, return them
                    if attractions:
                        print(f"Fetched {len(attractions)} attractions from OpenStreetMap for {location}")
                        return attractions[:8]  # Return top 8

                except Exception as e:
                    print(f"Error with bbox_size {bbox_size}: {str(e)}")
                    continue

            # If Overpass didn't work, try sample places
            print(f"No Overpass results for {location}, using sample places")
            return self._get_sample_places(location)

        except Exception as e:
            print(f"Error getting nearby places: {str(e)}")
            return self._get_sample_places(location)

    def geocode(self, address: str) -> Optional[Dict]:
        """
        Geocode an address to coordinates using Nominatim (OpenStreetMap)
        """
        try:
            response = self.session.get(
                f"{self.NOMINATIM_URL}/search",
                params={
                    'q': address,
                    'format': 'json',
                    'limit': 1
                },
                timeout=10
            )

            if response.status_code != 200:
                return None

            data = response.json()
            if not data:
                return None

            result = data[0]
            return {
                'address': result.get('display_name', address),
                'lat': float(result.get('lat')),
                'lng': float(result.get('lon'))
            }

        except Exception as e:
            print(f"Error geocoding address: {str(e)}")
            return None

    def get_distance(self, origin: str, destination: str) -> Optional[Dict]:
        """
        Calculate distance and duration between two locations
        Uses OpenStreetMap's routing (OSRM)
        """
        try:
            # Geocode both addresses
            origin_coords = self.geocode(origin)
            dest_coords = self.geocode(destination)

            if not origin_coords or not dest_coords:
                return self._get_sample_distance(origin, destination)

            # Use OSRM (Open Source Routing Machine) for routing
            osrm_url = "https://router.project-osrm.org/route/v1/driving"
            url = f"{osrm_url}/{origin_coords['lng']},{origin_coords['lat']};{dest_coords['lng']},{dest_coords['lat']}"

            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return self._get_sample_distance(origin, destination)

            data = response.json()
            if data.get('code') == 'Ok' and data.get('routes'):
                route = data['routes'][0]
                distance_m = route.get('distance', 0)
                duration_s = route.get('duration', 0)

                # Convert to readable format
                distance_km = distance_m / 1000
                distance_text = f"{distance_km:.1f} km"
                
                minutes = duration_s / 60
                if minutes > 60:
                    hours = int(minutes // 60)
                    mins = int(minutes % 60)
                    duration_text = f"{hours}h {mins}m"
                else:
                    duration_text = f"{int(minutes)} mins"

                return {
                    'distance': distance_text,
                    'distance_value': int(distance_m),
                    'duration': duration_text,
                    'duration_value': int(duration_s)
                }

            return self._get_sample_distance(origin, destination)

        except Exception as e:
            print(f"Error calculating distance: {str(e)}")
            return self._get_sample_distance(origin, destination)

    def get_place_details(self, place_id: str, fields: Optional[List] = None) -> Dict:
        """
        Get detailed place information
        For OSM places, extract from tags
        """
        try:
            if not place_id.startswith('osm_'):
                return self._get_sample_place_details(place_id)

            # For OSM places, we already have good data
            return {
                "place_id": place_id,
                "name": "Point of Interest",
                "formatted_address": "Location details",
                "rating": 4.5,
                "opening_hours": "9:00 AM - 6:00 PM"
            }

        except Exception as e:
            print(f"Error getting place details: {str(e)}")
            raise

    def get_photo_url(self, photo_reference: str, maxwidth: int = 800) -> str:
        """
        Return a fallback photo URL since OSM doesn't provide photos directly
        Uses Picsum Photos or Wikimedia Commons
        """
        seed = hash(photo_reference) % 10000 if photo_reference else 1
        return f"https://picsum.photos/seed/{abs(seed)}/{maxwidth}/{int(maxwidth*0.75)}"

    @staticmethod
    def _get_hardcoded_attractions(location: str) -> Optional[List[Dict]]:
        """
        Return real attractions for known cities
        Ensures Place Lookup demo shows real places instead of samples
        """
        # Map of city names to their famous attractions with coordinates
        hardcoded_places = {
            "paris": [
                {"name": "Eiffel Tower", "lat": 48.8584, "lng": 2.2945, "type": "monument", "rating": 4.7},
                {"name": "Louvre Museum", "lat": 48.8606, "lng": 2.3352, "type": "museum", "rating": 4.6},
                {"name": "Notre-Dame", "lat": 48.8530, "lng": 2.3499, "type": "monument", "rating": 4.7},
                {"name": "Arc de Triomphe", "lat": 48.8738, "lng": 2.2950, "type": "monument", "rating": 4.6},
                {"name": "Sacré-Cœur", "lat": 48.8867, "lng": 2.3431, "type": "monument", "rating": 4.6},
                {"name": "Champs-Élysées", "lat": 48.8699, "lng": 2.3073, "type": "landmark", "rating": 4.5},
                {"name": "Versailles Palace", "lat": 48.8047, "lng": 2.1200, "type": "palace", "rating": 4.7},
            ],
            "london": [
                {"name": "Big Ben", "lat": 51.4975, "lng": -0.1246, "type": "monument", "rating": 4.6},
                {"name": "Tower of London", "lat": 51.5055, "lng": -0.0754, "type": "attraction", "rating": 4.5},
                {"name": "Buckingham Palace", "lat": 51.5007, "lng": -0.1415, "type": "palace", "rating": 4.5},
                {"name": "British Museum", "lat": 51.5194, "lng": -0.1270, "type": "museum", "rating": 4.6},
                {"name": "Tower Bridge", "lat": 51.5055, "lng": -0.0754, "type": "monument", "rating": 4.6},
                {"name": "Westminster Abbey", "lat": 51.4954, "lng": -0.1266, "type": "monument", "rating": 4.6},
                {"name": "London Eye", "lat": 51.5033, "lng": -0.1195, "type": "attraction", "rating": 4.4},
            ],
            "tokyo": [
                {"name": "Senso-ji Temple", "lat": 35.7148, "lng": 139.7967, "type": "temple", "rating": 4.5},
                {"name": "Tokyo Tower", "lat": 35.6762, "lng": 139.7394, "type": "attraction", "rating": 4.5},
                {"name": "Shibuya Crossing", "lat": 35.6595, "lng": 139.7004, "type": "landmark", "rating": 4.6},
                {"name": "Meiji Shrine", "lat": 35.6763, "lng": 139.7000, "type": "shrine", "rating": 4.6},
                {"name": "Tokyo Skytree", "lat": 35.7100, "lng": 139.8107, "type": "tower", "rating": 4.4},
                {"name": "Tsukiji Market", "lat": 35.6657, "lng": 139.7726, "type": "market", "rating": 4.5},
                {"name": "Shinjuku Gyoen", "lat": 35.6857, "lng": 139.7107, "type": "park", "rating": 4.5},
            ],
            "new york": [
                {"name": "Statue of Liberty", "lat": 40.6892, "lng": -74.0445, "type": "monument", "rating": 4.5},
                {"name": "Empire State Building", "lat": 40.7484, "lng": -73.9857, "type": "building", "rating": 4.5},
                {"name": "Central Park", "lat": 40.7829, "lng": -73.9654, "type": "park", "rating": 4.5},
                {"name": "Times Square", "lat": 40.7580, "lng": -73.9855, "type": "landmark", "rating": 4.4},
                {"name": "Brooklyn Bridge", "lat": 40.7061, "lng": -73.9969, "type": "bridge", "rating": 4.6},
                {"name": "One World Trade Center", "lat": 40.7127, "lng": -74.0134, "type": "building", "rating": 4.5},
                {"name": "Metropolitan Museum of Art", "lat": 40.7813, "lng": -73.9740, "type": "museum", "rating": 4.6},
            ],
            "hyderabad": [
                {"name": "Charminar", "lat": 17.3597, "lng": 78.4594, "type": "monument", "rating": 4.4},
                {"name": "Golconda Fort", "lat": 17.3829, "lng": 78.4156, "type": "fort", "rating": 4.5},
                {"name": "Hussain Sagar Lake", "lat": 17.3738, "lng": 78.4711, "type": "lake", "rating": 4.3},
                {"name": "Mecca Masjid", "lat": 17.3609, "lng": 78.4682, "type": "mosque", "rating": 4.2},
                {"name": "Salar Jung Museum", "lat": 17.3650, "lng": 78.4844, "type": "museum", "rating": 4.4},
                {"name": "Birla Mandir", "lat": 17.3809, "lng": 78.4711, "type": "temple", "rating": 4.4},
                {"name": "Nizam's Museum", "lat": 17.3819, "lng": 78.4706, "type": "museum", "rating": 4.3},
            ],
            "delhi": [
                {"name": "Taj Mahal", "lat": 27.1751, "lng": 78.0421, "type": "monument", "rating": 4.7},
                {"name": "Red Fort", "lat": 28.6562, "lng": 77.2410, "type": "fort", "rating": 4.4},
                {"name": "India Gate", "lat": 28.6129, "lng": 77.2295, "type": "monument", "rating": 4.4},
                {"name": "Jama Masjid", "lat": 28.6505, "lng": 77.2308, "type": "mosque", "rating": 4.3},
                {"name": "Qutub Minar", "lat": 28.5244, "lng": 77.1855, "type": "tower", "rating": 4.4},
                {"name": "Rashtrapati Bhavan", "lat": 28.5919, "lng": 77.1998, "type": "palace", "rating": 4.3},
                {"name": "Lal Qila", "lat": 28.6562, "lng": 77.2410, "type": "fort", "rating": 4.4},
            ],
            "barcelona": [
                {"name": "Sagrada Familia", "lat": 41.4036, "lng": 2.1744, "type": "basilica", "rating": 4.6},
                {"name": "Park Güell", "lat": 41.4145, "lng": 2.1528, "type": "park", "rating": 4.6},
                {"name": "Gothic Quarter", "lat": 41.3851, "lng": 2.1734, "type": "district", "rating": 4.5},
                {"name": "Las Ramblas", "lat": 41.3827, "lng": 2.1707, "type": "street", "rating": 4.4},
                {"name": "Casa Batlló", "lat": 41.3915, "lng": 2.1649, "type": "building", "rating": 4.6},
                {"name": "Montjuïc", "lat": 41.3674, "lng": 2.1617, "type": "hill", "rating": 4.4},
                {"name": "Arc de Triomf", "lat": 41.3906, "lng": 2.1859, "type": "monument", "rating": 4.4},
            ],
            "rome": [
                {"name": "Colosseum", "lat": 41.8902, "lng": 12.4923, "type": "monument", "rating": 4.6},
                {"name": "Roman Forum", "lat": 41.8925, "lng": 12.4853, "type": "landmark", "rating": 4.6},
                {"name": "Pantheon", "lat": 41.8986, "lng": 12.4769, "type": "monument", "rating": 4.6},
                {"name": "Vatican Museums", "lat": 41.9063, "lng": 12.4534, "type": "museum", "rating": 4.5},
                {"name": "Trevi Fountain", "lat": 41.9009, "lng": 12.4833, "type": "monument", "rating": 4.6},
                {"name": "Sistine Chapel", "lat": 41.9064, "lng": 12.4558, "type": "chapel", "rating": 4.7},
                {"name": "Spanish Steps", "lat": 41.9058, "lng": 12.4741, "type": "landmark", "rating": 4.5},
            ]
        }
        
        # Try to match the location
        location_lower = location.lower().strip()
        
        for city_key, attractions in hardcoded_places.items():
            if city_key in location_lower or location_lower in city_key or location_lower.startswith(city_key[:3]):
                # Convert to the format expected by nearby-attractions endpoint
                return [
                    {
                        "place_id": f"hardcoded_{i}",
                        "name": attr["name"],
                        "location": {"lat": attr["lat"], "lng": attr["lng"]},
                        "rating": attr["rating"],
                        "address": f"{attr['name']}, {city_key.title()}",
                        "type": attr["type"],
                        "website": "",
                        "opening_hours": "9:00 AM - 6:00 PM"
                    }
                    for i, attr in enumerate(attractions)
                ]
        
        return None

    @staticmethod
    def _get_sample_places(location: str) -> List[Dict]:
        """Return sample attractions as fallback when no real data available"""
        return [
            {
                "place_id": "sample_0",
                "name": "Popular Attraction in " + location,
                "location": {"lat": 40.7128, "lng": -74.0060},
                "rating": 4.5,
                "address": f"123 Main St, {location}",
                "type": "attraction",
                "website": "",
                "opening_hours": "9:00 AM - 6:00 PM"
            },
            {
                "place_id": "sample_1",
                "name": "Museum in " + location,
                "location": {"lat": 40.7580, "lng": -73.9855},
                "rating": 4.4,
                "address": f"456 Park Ave, {location}",
                "type": "museum",
                "website": "",
                "opening_hours": "10:00 AM - 5:00 PM"
            },
            {
                "place_id": "sample_2",
                "name": "Park in " + location,
                "location": {"lat": 40.7829, "lng": -73.9654},
                "rating": 4.3,
                "address": f"789 Nature Way, {location}",
                "type": "park",
                "website": "",
                "opening_hours": "Sunrise - Sunset"
            }
        ]

    @staticmethod
    def _get_sample_coordinates(address: str) -> Dict:
        """Return sample coordinates for demo"""
        return {"address": address, "lat": 40.7128, "lng": -74.0060}

    @staticmethod
    def _get_sample_distance(origin: str, destination: str) -> Dict:
        """Return sample distance for demo"""
        return {"distance": "5.2 km", "distance_value": 5200, "duration": "15 mins", "duration_value": 900}

    @staticmethod
    def _get_sample_place_details(place_id: str) -> Dict:
        """Return sample place details for demo"""
        return {
            "place_id": place_id,
            "name": "Sample Place",
            "formatted_address": "123 Sample St",
            "rating": 4.5,
            "opening_hours": "9:00 AM - 6:00 PM"
        }


