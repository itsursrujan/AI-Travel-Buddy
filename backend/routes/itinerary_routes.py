# backend/routes/itinerary_routes.py
from flask import Blueprint, request, jsonify
from database import MongoDatabase
from models.itinerary_model import Itinerary
from services.jwt_handler import JWTHandler
from services.ai_engine import AIEngine
from services.bigquery_service import BigQueryService
from bson.objectid import ObjectId

itinerary_bp = Blueprint("itinerary", __name__, url_prefix="/api/itinerary")
bigquery_service = BigQueryService()

@itinerary_bp.route("/generate", methods=["POST"])
def generate_itinerary():
    """Generate AI-powered itinerary"""
    try:
        auth_header = request.headers.get("Authorization")
        token = JWTHandler.get_token_from_header(auth_header)

        if not token:
            return jsonify({"error": "Token required"}), 401

        payload = JWTHandler.verify_token(token)
        if "error" in payload:
            return jsonify(payload), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400
            
        destination = data.get("destination")
        budget = data.get("budget")
        days = data.get("days", 3)
        travel_style = data.get("travel_style", "leisure")

        if not all([destination, budget]):
            return jsonify({"error": "Destination and budget required"}), 400
        
        # Validate input types
        try:
            budget = float(budget)
            days = int(days)
            if budget <= 0:
                return jsonify({"error": "Budget must be greater than 0"}), 400
            if days < 1 or days > 30:
                return jsonify({"error": "Days must be between 1 and 30"}), 400
            if travel_style not in ["leisure", "adventure", "cultural", "budget"]:
                return jsonify({"error": "Invalid travel style"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid input format"}), 400

        # Generate itinerary using AI engine
        ai_engine = AIEngine()
        # Check if OpenAI key is set, otherwise use sample
        from config import Config
        if Config.OPENAI_API_KEY:
            itinerary_data = ai_engine.generate_itinerary(destination, budget, days, travel_style)
        else:
            itinerary_data = ai_engine.get_sample_itinerary(destination, budget, days, travel_style)

        # Create itinerary document
        itinerary_doc = Itinerary.create(
            payload["user_id"],
            destination,
            budget,
            days,
            travel_style,
            itinerary_data
        )

        # Save to database
        db = MongoDatabase.get_db()
        result = db.itineraries.insert_one(itinerary_doc)
        
        # Log to BigQuery
        try:
            total_cost = itinerary_data.get("estimated_cost", budget) if itinerary_data else budget
            bigquery_service.log_itinerary(
                itinerary_id=str(result.inserted_id),
                user_id=payload["user_id"],
                destination=destination,
                budget=budget,
                days=days,
                travel_style=travel_style,
                total_cost=total_cost
            )
            bigquery_service.log_event(
                user_id=payload["user_id"],
                event_type="itinerary_created",
                destination=destination,
                metadata={"days": days, "travel_style": travel_style}
            )
        except Exception as bq_error:
            print(f"⚠ BigQuery logging failed: {str(bq_error)}")

        return jsonify({
            "message": "Itinerary generated successfully",
            "itinerary": Itinerary.to_dict({**itinerary_doc, "_id": result.inserted_id})
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@itinerary_bp.route("/generate-public", methods=["POST"])
def generate_itinerary_public():
    """Generate AI-powered itinerary without authentication (for WordPress widget/public use)
    
    This endpoint allows public access for embedding in WordPress sites.
    Consider adding rate limiting in production.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400
            
        destination = data.get("destination")
        budget = data.get("budget")
        days = data.get("days", 3)
        travel_style = data.get("travel_style", "leisure")

        if not all([destination, budget]):
            return jsonify({"error": "Destination and budget required"}), 400
        
        # Validate input types
        try:
            budget = float(budget)
            days = int(days)
            if budget <= 0:
                return jsonify({"error": "Budget must be greater than 0"}), 400
            if days < 1 or days > 30:
                return jsonify({"error": "Days must be between 1 and 30"}), 400
            if travel_style not in ["leisure", "adventure", "cultural", "budget"]:
                return jsonify({"error": "Invalid travel style"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid input format"}), 400

        # Generate itinerary using AI engine
        ai_engine = AIEngine()
        from config import Config
        if Config.OPENAI_API_KEY:
            itinerary_data = ai_engine.generate_itinerary(destination, budget, days, travel_style)
        else:
            itinerary_data = ai_engine.get_sample_itinerary(destination, budget, days, travel_style)

        # Return itinerary without saving to database (public use)
        # Optionally, you could save with a guest user_id or skip saving entirely
        return jsonify({
            "message": "Itinerary generated successfully",
            "itinerary": {
                "destination": destination,
                "budget": {"amount": budget, "currency": "USD"},
                "travel_duration": days,
                "travel_style": travel_style,
                "itinerary": itinerary_data,
                "is_public": True
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@itinerary_bp.route("/save", methods=["POST"])
def save_itinerary():
    """Save an itinerary provided by the client for the authenticated user.

    Expected JSON payload:
    {
        "destination": "Paris",
        "budget": 1200,
        "days": 3,
        "travel_style": "leisure",
        "itinerary": { ... }  # full itinerary object (days, tourist_spots, tips, etc.)
        "is_public": false  # optional
    }
    """
    try:
        auth_header = request.headers.get("Authorization")
        token = JWTHandler.get_token_from_header(auth_header)

        if not token:
            return jsonify({"error": "Token required"}), 401

        payload = JWTHandler.verify_token(token)
        if "error" in payload:
            return jsonify(payload), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400
            
        destination = data.get("destination")
        budget = data.get("budget")
        days = data.get("days", 1)
        travel_style = data.get("travel_style", "leisure")
        itinerary_data = data.get("itinerary")
        is_public = bool(data.get("is_public", False))

        if not all([destination, budget, itinerary_data]):
            return jsonify({"error": "destination, budget and itinerary are required"}), 400
        
        # Validate input types
        try:
            budget = float(budget)
            days = int(days)
            if budget <= 0:
                return jsonify({"error": "Budget must be greater than 0"}), 400
            if days < 1 or days > 30:
                return jsonify({"error": "Days must be between 1 and 30"}), 400
            if travel_style not in ["leisure", "adventure", "cultural", "budget"]:
                return jsonify({"error": "Invalid travel style"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid input format"}), 400

        user_id = payload.get("user_id")

        # Create itinerary document
        itinerary_doc = Itinerary.create(user_id, destination, budget, days, travel_style, itinerary_data)
        itinerary_doc["is_public"] = is_public

        # Save to DB
        db = MongoDatabase.get_db()
        result = db.itineraries.insert_one(itinerary_doc)

        return jsonify({
            "message": "Itinerary saved successfully",
            "itinerary": Itinerary.to_dict({**itinerary_doc, "_id": result.inserted_id})
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@itinerary_bp.route("/user/<user_id>", methods=["GET"])
def get_user_itineraries(user_id):
    """Get all itineraries for a user"""
    try:
        auth_header = request.headers.get("Authorization")
        token = JWTHandler.get_token_from_header(auth_header)

        if not token:
            return jsonify({"error": "Token required"}), 401

        payload = JWTHandler.verify_token(token)
        if "error" in payload:
            return jsonify(payload), 401

        # Validate ObjectId format
        try:
            ObjectId(user_id)
        except Exception:
            return jsonify({"error": "Invalid user ID format"}), 400

        # Verify user can only access their own itineraries (unless admin)
        if payload["user_id"] != user_id and payload.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        db = MongoDatabase.get_db()
        itineraries = list(db.itineraries.find(
            {"user_id": ObjectId(user_id)},
            sort=[("created_at", -1)]
        ))

        return jsonify({
            "itineraries": [Itinerary.to_dict(it) for it in itineraries]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@itinerary_bp.route("/<itinerary_id>", methods=["GET"])
def get_itinerary(itinerary_id):
    """Get a specific itinerary by ID"""
    try:
        db = MongoDatabase.get_db()
        itinerary = db.itineraries.find_one({"_id": ObjectId(itinerary_id)})

        if not itinerary:
            return jsonify({"error": "Itinerary not found"}), 404

        # Increment views
        db.itineraries.update_one(
            {"_id": ObjectId(itinerary_id)},
            {"$inc": {"views": 1}}
        )

        return jsonify(Itinerary.to_dict(itinerary)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@itinerary_bp.route("/<itinerary_id>", methods=["DELETE"])
def delete_itinerary(itinerary_id):
    """Delete an itinerary"""
    try:
        auth_header = request.headers.get("Authorization")
        token = JWTHandler.get_token_from_header(auth_header)

        if not token:
            return jsonify({"error": "Token required"}), 401

        payload = JWTHandler.verify_token(token)
        if "error" in payload:
            return jsonify(payload), 401

        # Validate ObjectId format
        try:
            ObjectId(itinerary_id)
        except Exception:
            return jsonify({"error": "Invalid itinerary ID format"}), 400

        db = MongoDatabase.get_db()
        
        # Check if itinerary exists and user has permission
        itinerary = db.itineraries.find_one({"_id": ObjectId(itinerary_id)})
        if not itinerary:
            return jsonify({"error": "Itinerary not found"}), 404
        
        # Allow deletion if user owns it or is admin
        if str(itinerary["user_id"]) != payload["user_id"] and payload.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        result = db.itineraries.delete_one({
            "_id": ObjectId(itinerary_id),
            "user_id": ObjectId(payload["user_id"])
        })

        if result.deleted_count == 0:
            # If admin, try deleting without user_id check
            if payload.get("role") == "admin":
                result = db.itineraries.delete_one({"_id": ObjectId(itinerary_id)})
                if result.deleted_count == 0:
                    return jsonify({"error": "Failed to delete itinerary"}), 500
            else:
                return jsonify({"error": "Itinerary not found or unauthorized"}), 404

        return jsonify({"message": "Itinerary deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


