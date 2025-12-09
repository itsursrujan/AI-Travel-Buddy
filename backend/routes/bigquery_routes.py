# backend/routes/bigquery_routes.py
from flask import Blueprint, jsonify, request
from services.bigquery_service import BigQueryService
from functools import wraps
import jwt
import os

bigquery_bp = Blueprint('bigquery', __name__, url_prefix='/api/analytics')
bigquery_service = BigQueryService()

# Simple token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Missing token"}), 401
        
        try:
            # Extract token from "Bearer <token>"
            if token.startswith('Bearer '):
                token = token[7:]
            
            secret = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
            decoded = jwt.decode(token, secret, algorithms=['HS256'])
            request.user = decoded
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated

@bigquery_bp.route('/popular-destinations', methods=['GET'])
def get_popular_destinations():
    """Get most popular travel destinations"""
    try:
        limit = request.args.get('limit', 10, type=int)
        destinations = bigquery_service.get_popular_destinations(limit)
        return jsonify({
            "success": True,
            "data": destinations
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bigquery_bp.route('/travel-style-stats', methods=['GET'])
def get_travel_style_stats():
    """Get travel style statistics"""
    try:
        stats = bigquery_service.get_travel_style_stats()
        return jsonify({
            "success": True,
            "data": stats
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bigquery_bp.route('/user-insights', methods=['GET'])
@token_required
def get_user_insights():
    """Get user-specific analytics"""
    try:
        user_id = request.user.get('user_id')
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID not found in token"
            }), 400
        
        insights = bigquery_service.get_user_insights(user_id)
        return jsonify({
            "success": True,
            "data": insights
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bigquery_bp.route('/top-attractions', methods=['GET'])
def get_top_attractions():
    """Get most popular attractions"""
    try:
        limit = request.args.get('limit', 10, type=int)
        attractions = bigquery_service.get_top_attractions(limit)
        return jsonify({
            "success": True,
            "data": attractions
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
