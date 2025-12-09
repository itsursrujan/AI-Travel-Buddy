# backend/services/jwt_handler.py
import jwt
from datetime import datetime, timedelta
from config import Config

class JWTHandler:
    """JWT token generation and verification"""

    @staticmethod
    def generate_token(user_id, email, role="traveler"):
        """Generate JWT token for user"""
        payload = {
            "user_id": str(user_id),
            "email": email,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXPIRY)
        }
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
        return token

    @staticmethod
    def verify_token(token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}

    @staticmethod
    def get_token_from_header(auth_header):
        """Extract token from Authorization header"""
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header.split(" ")[1]


