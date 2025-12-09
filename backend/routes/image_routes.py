# backend/routes/image_routes.py
from flask import Blueprint, request, jsonify
from services.image_service import ImageService

image_bp = Blueprint("images", __name__, url_prefix="/api/images")

@image_bp.route("/landmark", methods=["GET"])
def get_landmark_image():
    """Get landmark image URL from Pexels API"""
    try:
        name = request.args.get("name")
        destination = request.args.get("destination", "")
        
        if not name:
            return jsonify({"error": "Landmark name required"}), 400
        
        # Get image from Pexels API
        image_url = ImageService.get_landmark_image(name, destination)
        
        if not image_url:
            return jsonify({"error": "Image not found"}), 404
        
        return jsonify({
            "success": True,
            "landmark": name,
            "destination": destination,
            "image_url": image_url
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
