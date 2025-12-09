# backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from database import MongoDatabase
from models.user_model import User
from services.jwt_handler import JWTHandler
from bson.objectid import ObjectId
from services.google_oauth import verify_id_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400
            
        email = data.get("email", "").strip().lower()
        password = data.get("password")
        name = data.get("name", "").strip()

        if not all([email, password, name]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Basic email validation
        if "@" not in email or "." not in email.split("@")[1]:
            return jsonify({"error": "Invalid email format"}), 400
        
        # Password length validation
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        db = MongoDatabase.get_db()
        
        # Check if user exists
        if db.users.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 409

        # Create user
        user_doc = User.create(email, password, name)
        result = db.users.insert_one(user_doc)

        # Generate token
        token = JWTHandler.generate_token(result.inserted_id, email, "traveler")

        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": User.to_dict({**user_doc, "_id": result.inserted_id})
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400
            
        email = data.get("email", "").strip().lower()
        password = data.get("password")

        if not all([email, password]):
            return jsonify({"error": "Email and password required"}), 400

        db = MongoDatabase.get_db()
        user = db.users.find_one({"email": email})

        if not user or not User.verify_password(user["password"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate token
        token = JWTHandler.generate_token(user["_id"], user["email"], user.get("role", "traveler"))

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": User.to_dict(user)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Get current user profile"""
    try:
        auth_header = request.headers.get("Authorization")
        token = JWTHandler.get_token_from_header(auth_header)

        if not token:
            return jsonify({"error": "Token required"}), 401

        payload = JWTHandler.verify_token(token)
        if "error" in payload:
            return jsonify(payload), 401

        db = MongoDatabase.get_db()
        user = db.users.find_one({"_id": ObjectId(payload["user_id"])})

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(User.to_dict(user)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/google', methods=['POST'])
def google_signin():
    """Sign in or register a user using Google ID token.

    Expects JSON: { "id_token": "..." }
    Returns JWT token and user record.
    """
    try:
        data = request.get_json() or {}
        id_token = data.get('id_token')
        if not id_token:
            return jsonify({'error': 'id_token required'}), 400

        # Verify token with Google
        payload = verify_id_token(id_token)

        email = payload.get('email')
        name = payload.get('name') or payload.get('email')
        picture = payload.get('picture')

        if not email:
            return jsonify({'error': 'Google token did not contain email'}), 400

        db = MongoDatabase.get_db()

        # Upsert user
        from datetime import datetime
        existing = db.users.find_one({'email': email})
        if existing:
            user = existing
            user_id = existing['_id']
            # Update picture if provided and not set
            if picture and not existing.get('picture'):
                db.users.update_one({'_id': user_id}, {'$set': {'picture': picture}})
                user = db.users.find_one({'_id': user_id})
        else:
            user_doc = {
                'email': email,
                'name': name,
                'picture': picture,
                'auth_provider': 'google',
                'role': 'traveler',
                'preferences': {
                    'travel_style': 'leisure',
                    'budget_currency': 'USD',
                    'notifications': True
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_active': True
            }
            res = db.users.insert_one(user_doc)
            user_id = res.inserted_id
            user = db.users.find_one({'_id': user_id})

        token = JWTHandler.generate_token(user_id, email, user.get('role', 'traveler'))

        return jsonify({'message': 'Google sign-in successful', 'token': token, 'user': User.to_dict(user)}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


