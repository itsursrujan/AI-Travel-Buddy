# backend/routes/analytics_routes.py
from flask import Blueprint, request, jsonify
from database import MongoDatabase
from services.jwt_handler import JWTHandler
from bson.objectid import ObjectId
# BigQuery integration removed per user request

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/trends", methods=["GET"])
def get_travel_trends():
    """Get travel trends from itineraries"""
    try:
        db = MongoDatabase.get_db()

        # Get top destinations
        top_destinations = list(db.itineraries.aggregate([
            {"$group": {
                "_id": "$destination",
                "count": {"$sum": 1},
                "avg_budget": {"$avg": "$budget.amount"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]))

        # Get average budget by travel style
        budget_by_style = list(db.itineraries.aggregate([
            {"$group": {
                "_id": "$travel_style",
                "avg_budget": {"$avg": "$budget.amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]))

        return jsonify({
            "top_destinations": top_destinations,
            "budget_by_travel_style": budget_by_style
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/stats", methods=["GET"])
def get_overall_stats():
    """Get overall statistics (total users, itineraries, views, likes, avg budget)"""
    try:
        auth_header = request.headers.get("Authorization")
        token = JWTHandler.get_token_from_header(auth_header)

        if not token:
            return jsonify({"error": "Token required"}), 401

        payload = JWTHandler.verify_token(token)
        if "error" in payload:
            return jsonify(payload), 401

        # Check if user is admin
        db = MongoDatabase.get_db()
        user = db.users.find_one({"_id": ObjectId(payload["user_id"])})
        if not user or user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403

        # Get total users
        total_users = db.users.count_documents({"is_active": {"$ne": False}})

        # Get itinerary stats
        itinerary_stats = list(db.itineraries.aggregate([
            {"$group": {
                "_id": None,
                "total_itineraries": {"$sum": 1},
                "total_views": {"$sum": "$views"},
                "total_likes": {"$sum": "$likes"},
                "avg_budget": {"$avg": "$budget.amount"}
            }}
        ]))

        if itinerary_stats:
            stats = itinerary_stats[0]
            return jsonify({
                "total_users": total_users,
                "total_itineraries": stats.get("total_itineraries", 0),
                "total_views": stats.get("total_views", 0),
                "total_likes": stats.get("total_likes", 0),
                "avg_budget": stats.get("avg_budget", 0)
            }), 200
        else:
            return jsonify({
                "total_users": total_users,
                "total_itineraries": 0,
                "total_views": 0,
                "total_likes": 0,
                "avg_budget": 0
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/user/<user_id>/stats", methods=["GET"])
def get_user_stats(user_id):
    """Get user statistics"""
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

        # Verify user can only access their own stats (unless admin)
        if payload["user_id"] != user_id and payload.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        db = MongoDatabase.get_db()

        # Get user itineraries stats
        stats = db.itineraries.aggregate([
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$group": {
                "_id": "$user_id",
                "total_itineraries": {"$sum": 1},
                "total_spent": {"$sum": "$budget.amount"},
                "avg_budget": {"$avg": "$budget.amount"},
                "total_views": {"$sum": "$views"},
                "total_likes": {"$sum": "$likes"}
            }}
        ])

        stats_list = list(stats)
        if not stats_list:
            return jsonify({
                "total_itineraries": 0,
                "total_spent": 0,
                "avg_budget": 0,
                "total_views": 0,
                "total_likes": 0
            }), 200

        return jsonify(stats_list[0]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# BigQuery ingestion removed per user request


