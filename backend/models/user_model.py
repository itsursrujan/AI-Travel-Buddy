# backend/models/user_model.py
from datetime import datetime
from bson.objectid import ObjectId
import bcrypt

class User:
    """User model for authentication and profile"""

    @staticmethod
    def create(email, password, name, role="traveler"):
        """Create a new user document"""
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return {
            "_id": ObjectId(),
            "email": email,
            "password": hashed_password,
            "name": name,
            "role": role,  # traveler, admin, content_manager, super_admin
            "preferences": {
                "travel_style": "leisure",
                "budget_currency": "USD",
                "notifications": True
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }

    @staticmethod
    def verify_password(stored_hash, password):
        """Verify password against stored hash"""
        try:
            # Handle both bytes and string hash formats
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode("utf-8")
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False

    @staticmethod
    def to_dict(user):
        """Convert user document to dict for JSON response (exclude password)"""
        user_dict = dict(user)
        user_dict.pop("password", None)
        user_dict["_id"] = str(user_dict["_id"])
        return user_dict


