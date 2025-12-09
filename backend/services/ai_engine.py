# backend/services/ai_engine.py
from openai import OpenAI
from config import Config
from .image_service import ImageService
import json
import requests
from bs4 import BeautifulSoup

class AIEngine:
    """AI-powered itinerary generation using OpenAI"""

    def __init__(self):
        # Initialize OpenAI client with API key only
        if Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.client = None

    def generate_itinerary(self, destination, budget, days, travel_style):
        """
        Generate an AI-powered itinerary for given parameters
        
        Args:
            destination (str): Travel destination (city/country)
            budget (int): Budget in USD
            days (int): Number of days for the trip
            travel_style (str): travel_style (leisure, adventure, cultural, budget)
        
        Returns:
            dict: Generated itinerary with daily plans and tourist spots
        """
        # FIRST: Fetch real attractions from the internet
        real_attractions = self.fetch_attractions_from_internet(destination)
        print(f"Fetched {len(real_attractions)} real attractions for {destination}")
        
        # Format attractions for AI prompt
        attractions_list = "\n".join([
            f"- {attr.get('name', 'Unknown')}: {attr.get('description', 'Tourist attraction')}"
            for attr in real_attractions[:8]
        ])
        
        prompt = f"""Generate a {days}-day travel itinerary for {destination} with a budget of ${budget} USD. 
        Travel style: {travel_style}.
        
        IMPORTANT: You MUST ONLY use the following REAL tourist attractions from {destination}:
{attractions_list}

        Create an itinerary that includes visits to these REAL attractions. Do NOT invent or hallucinate attraction names.
        Use ONLY the attraction names listed above.
        
        Provide the response in JSON format with the following structure:
        {{
            "title": "itinerary title",
            "days": [
                {{
                    "day": 1,
                    "title": "day title",
                    "activities": [
                        {{
                            "time": "09:00 AM",
                            "activity": "activity description (include actual attraction names when visiting places)",
                            "cost": "estimated cost",
                            "duration": "duration in hours"
                        }}
                    ],
                    "meals": {{
                        "breakfast": "recommendation",
                        "lunch": "recommendation",
                        "dinner": "recommendation"
                    }},
                    "total_cost": "estimated daily cost"
                }}
            ],
            "tourist_spots": [
                {{
                    "name": "EXACT name from the provided list",
                    "description": "Brief description of the attraction",
                    "ticket_price": "Price in USD",
                    "opening_hours": "Opening hours",
                    "image_url": "placeholder"
                }}
            ],
            "tips": ["travel tip 1", "travel tip 2"],
            "estimated_total_cost": "total trip cost estimate"
        }}
        
        CRITICAL: tourist_spots array MUST contain REAL attractions from the list above. Do NOT invent attractions.
        Make sure the itinerary fits within the given budget. Include 5-7 real tourist spots from the provided list."""
        
        try:
            # If no API key, return sample itinerary
            if not self.client:
                return self.get_sample_itinerary(destination, budget, days, travel_style)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a travel planning expert. You MUST ONLY use the real tourist attractions provided in the user's message. Never invent or hallucinate attraction names. Always use the exact names provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content
            # Find JSON in response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                try:
                    itinerary = json.loads(json_str)
                    
                    # Validate itinerary structure
                    if not isinstance(itinerary, dict):
                        raise ValueError("Invalid itinerary format")
                    
                    # Ensure required fields exist
                    if "days" not in itinerary:
                        itinerary["days"] = []
                    if "tourist_spots" not in itinerary:
                        itinerary["tourist_spots"] = real_attractions[:6]  # Use real attractions as fallback
                    if "tips" not in itinerary:
                        itinerary["tips"] = []
                    
                    # Validate tourist spots are from real attractions
                    if "tourist_spots" in itinerary and itinerary["tourist_spots"]:
                        real_spot_names = {attr.get("name", "").lower() for attr in real_attractions}
                        validated_spots = []
                        
                        for spot in itinerary["tourist_spots"]:
                            if not isinstance(spot, dict):
                                continue
                            
                            spot_name = spot.get("name", "").strip()
                            
                            # Try exact match first
                            matched_attraction = None
                            for real_attr in real_attractions:
                                if real_attr.get("name", "").lower() == spot_name.lower():
                                    matched_attraction = real_attr
                                    break
                            
                            # If matched, use real data
                            if matched_attraction:
                                spot["name"] = matched_attraction.get("name", spot_name)
                                spot["description"] = matched_attraction.get("description", spot.get("description", ""))
                                spot["image_url"] = matched_attraction.get("image_url", spot.get("image_url", "placeholder"))
                                if not spot.get("ticket_price"):
                                    spot["ticket_price"] = matched_attraction.get("ticket_price", "$15-25")
                                if not spot.get("opening_hours"):
                                    spot["opening_hours"] = matched_attraction.get("opening_hours", "9:00 AM - 6:00 PM")
                                validated_spots.append(spot)
                            else:
                                # If spot name doesn't match real attractions, try to find similar one
                                if len(real_attractions) > 0:
                                    # Use a real attraction instead
                                    similar_attr = real_attractions[len(validated_spots) % len(real_attractions)]
                                    spot["name"] = similar_attr.get("name", spot_name)
                                    spot["description"] = similar_attr.get("description", "")
                                    spot["image_url"] = similar_attr.get("image_url", "placeholder")
                                    spot["ticket_price"] = similar_attr.get("ticket_price", "$15-25")
                                    spot["opening_hours"] = similar_attr.get("opening_hours", "9:00 AM - 6:00 PM")
                                    validated_spots.append(spot)
                        
                        # Ensure we have enough spots
                        if len(validated_spots) < len(real_attractions):
                            for i in range(len(validated_spots), min(6, len(real_attractions))):
                                validated_spots.append(real_attractions[i])
                        
                        itinerary["tourist_spots"] = validated_spots[:8]
                    else:
                        itinerary["tourist_spots"] = real_attractions[:6]
                    
                    return itinerary
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    return self.get_sample_itinerary(destination, budget, days, travel_style)
            else:
                # Fallback to sample itinerary if parsing fails
                return self.get_sample_itinerary(destination, budget, days, travel_style)
                
        except Exception as e:
            print(f"Error generating itinerary: {str(e)}")
            # Fallback to sample itinerary on error
            return self.get_sample_itinerary(destination, budget, days, travel_style)

    @staticmethod
    def fetch_attractions_from_internet(destination):
        """
        Fetch real tourist attractions for a destination
        Uses hardcoded database of famous landmarks as primary source
        """
        real_attractions = []
        
        # HARDCODED DATABASE OF FAMOUS LANDMARKS - PRIMARY SOURCE
        popular_destinations = {
            "paris": ["Eiffel Tower", "Louvre Museum", "Notre-Dame", "Arc de Triomphe", "Sacré-Cœur", "Champs-Élysées", "Versailles"],
            "london": ["Big Ben", "Tower of London", "Buckingham Palace", "British Museum", "Tower Bridge", "Westminster Abbey", "London Eye"],
            "tokyo": ["Senso-ji Temple", "Tokyo Tower", "Shibuya Crossing", "Meiji Shrine", "Tsukiji Market", "Tokyo Skytree", "Shinjuku Gyoen"],
            "new york": ["Statue of Liberty", "Empire State Building", "Central Park", "Times Square", "Brooklyn Bridge", "One World Trade Center", "Museum of Natural History"],
            "hyderabad": ["Charminar", "Golconda Fort", "Hussain Sagar Lake", "Mecca Masjid", "Salar Jung Museum", "Birla Mandir", "Nizam's Museum"],
            "delhi": ["Taj Mahal", "Red Fort", "India Gate", "Jama Masjid", "Qutub Minar", "Rashtrapati Bhavan", "Lal Qila"],
            "barcelona": ["Sagrada Familia", "Park Güell", "Gothic Quarter", "Las Ramblas", "Casa Batlló", "Montjuïc", "Arc de Triomf"],
            "rome": ["Colosseum", "Roman Forum", "Pantheon", "Vatican Museums", "Trevi Fountain", "Sistine Chapel", "Spanish Steps"],
            "dubai": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah", "Gold Souk", "Sheikh Mohammed Centre", "Dubai Marina", "Jumeirah Beach"],
            "mumbai": ["Gateway of India", "Marine Drive", "Taj Mahal Palace", "Elephanta Caves", "Haji Ali", "CST Station", "Siddhivinayak Temple"],
        }
        
        # Try to match destination with hardcoded list
        dest_lower = destination.lower().strip()
        matched_attractions = None
        
        for known_dest, attractions in popular_destinations.items():
            if known_dest in dest_lower or dest_lower in known_dest or dest_lower.startswith(known_dest[:3]):
                matched_attractions = attractions
                print(f"Using hardcoded attractions for {destination}")
                break
        
        # If we found a match, use it
        if matched_attractions:
            for attraction_name in matched_attractions[:8]:
                real_attractions.append({
                    "name": attraction_name,
                    "description": f"Famous tourist attraction in {destination}",
                    "ticket_price": "$15-25",
                    "opening_hours": "9:00 AM - 6:00 PM",
                    "image_url": ImageService.get_landmark_image(attraction_name, destination)
                })
            print(f"Fetched {len(real_attractions)} hardcoded attractions for {destination}")
            return real_attractions
        
        # FALLBACK: Try OpenStreetMap API for unknown destinations
        try:
            from .maps_service import MapsService
            maps_service = MapsService()
            nearby_places = maps_service.get_nearby_places(destination, radius=15000)
            
            if nearby_places and len(nearby_places) > 0:
                # Filter and deduplicate results
                for place in nearby_places:
                    place_name = place.get("name", "").strip()
                    
                    # Skip duplicates and generic names
                    if place_name.lower() in [attr["name"].lower() for attr in real_attractions]:
                        continue
                    if not place_name or len(place_name) < 3:
                        continue
                    
                    real_attractions.append({
                        "name": place_name,
                        "description": place.get("address", f"Tourist attraction in {destination}"),
                        "ticket_price": "$15-25",
                        "opening_hours": "9:00 AM - 6:00 PM",
                        "rating": str(place.get("rating", "4.5")),
                        "image_url": ImageService.get_landmark_image(place_name, destination)
                    })
                    
                    if len(real_attractions) >= 8:
                        break
                
                if len(real_attractions) >= 5:
                    print(f"Fetched {len(real_attractions)} attractions from OpenStreetMap for {destination}")
                    return real_attractions
        
        except Exception as e:
            print(f"Error fetching from OpenStreetMap: {str(e)}")
        
        # If still no attractions found, return generic fallback
        print(f"No attractions found for {destination}, returning generic fallback")
        for i in range(5):
            real_attractions.append({
                "name": f"Popular Attraction {i+1}",
                "description": f"Tourist spot in {destination}",
                "ticket_price": "$15-25",
                "opening_hours": "9:00 AM - 6:00 PM",
                "image_url": ImageService.get_landmark_image(f"landmark", destination)
            })
        
        return real_attractions

    @staticmethod
    def get_sample_itinerary(destination, budget, days, travel_style):
        """
        Return a sample itinerary for demo purposes (when API key is not set)
        Fetches real attractions from the internet
        """
        # Fetch real attractions from internet sources
        real_attractions = AIEngine.fetch_attractions_from_internet(destination)
        
        return {
            "title": f"{days} Days in {destination}",
            "destination": destination,
            "budget": budget,
            "currency": "USD",
            "days": [
                {
                    "day": i + 1,
                    "title": f"Day {i + 1}: Exploring {destination}",
                    "activities": [
                        {
                            "time": "08:00 AM",
                            "activity": f"Breakfast at local cafe",
                            "cost": f"${budget // days // 4}",
                            "duration": "1 hour"
                        },
                        {
                            "time": "10:00 AM",
                            "activity": f"Visit major attraction in {destination}",
                            "cost": f"${budget // days // 3}",
                            "duration": "3 hours"
                        },
                        {
                            "time": "01:00 PM",
                            "activity": "Lunch at restaurant",
                            "cost": f"${budget // days // 4}",
                            "duration": "1.5 hours"
                        },
                        {
                            "time": "03:00 PM",
                            "activity": f"Local exploration & shopping",
                            "cost": f"${budget // days // 5}",
                            "duration": "2 hours"
                        },
                        {
                            "time": "07:00 PM",
                            "activity": "Dinner & evening entertainment",
                            "cost": f"${budget // days // 3}",
                            "duration": "2 hours"
                        }
                    ],
                    "meals": {
                        "breakfast": "Local cafe specialties",
                        "lunch": "Traditional restaurant",
                        "dinner": "Fine dining experience"
                    },
                    "total_cost": f"${budget // days}"
                }
                for i in range(days)
            ],
            "tips": [
                f"Best time to visit {destination} is during shoulder seasons",
                "Use public transportation to save on costs",
                "Book attractions in advance for discounts",
                "Try local cuisine for authentic experience",
                "Visit free attractions and parks"
            ],
            "tourist_spots": real_attractions,
            "estimated_total_cost": f"${budget}"
        }


