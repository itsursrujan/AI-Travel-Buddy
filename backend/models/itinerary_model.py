# backend/models/itinerary_model.py
from datetime import datetime
from bson.objectid import ObjectId

class Itinerary:
    """Itinerary model for AI-generated trip plans"""

    @staticmethod
    def create(user_id, destination, budget, travel_duration, travel_style, itinerary_data):
        """Create a new itinerary document"""
        return {
            "_id": ObjectId(),
            "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
            "destination": destination,
            "budget": {
                "amount": budget,
                "currency": "USD"
            },
            "travel_duration": travel_duration,  # in days
            "travel_style": travel_style,  # leisure, adventure, cultural, budget
            "itinerary": itinerary_data,  # AI-generated itinerary
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_public": False,
            "views": 0,
            "likes": 0,
            "status": "draft"  # draft, published, archived
        }

    @staticmethod
    def to_dict(itinerary):
        """Convert itinerary document to dict for JSON response"""
        itinerary_dict = dict(itinerary)
        itinerary_dict["_id"] = str(itinerary_dict["_id"])
        itinerary_dict["user_id"] = str(itinerary_dict["user_id"])
        return itinerary_dict


