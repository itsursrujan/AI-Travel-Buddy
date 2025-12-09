# backend/routes/maps_routes.py
from flask import Blueprint, request, jsonify
from services.maps_service import MapsService
from services.image_service import ImageService
from flask import Response
import requests
from services.cache_service import default_cache

maps_bp = Blueprint("maps", __name__, url_prefix="/api/maps")

@maps_bp.route("/nearby-attractions", methods=["GET"])
def get_nearby_attractions():
    """Get nearby attractions for a location using OpenStreetMap"""
    try:
        location = request.args.get("location")
        radius = request.args.get("radius", 5000, type=int)

        if not location:
            return jsonify({"error": "Location required"}), 400

        # Use OpenStreetMap to get nearby attractions
        maps_service = MapsService()
        attractions = maps_service.get_nearby_places(location, radius)

        return jsonify({
            "location": location,
            "source": "openstreetmap",
            "attractions": attractions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@maps_bp.route("/place-details", methods=["GET"])
def place_details():
    """Get detailed place information by place_id"""
    try:
        place_id = request.args.get("place_id")
        if not place_id:
            return jsonify({"error": "place_id required"}), 400

        maps_service = MapsService()
        details = maps_service.get_place_details(place_id)
        return jsonify(details), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@maps_bp.route("/photo", methods=["GET"])
def photo_proxy():
    """Proxy a Google Place Photo request by photo_reference to hide API key.

    Query params: photo_reference (required), maxwidth (optional)
    """
    try:
        photo_ref = request.args.get("photo_reference")
        maxwidth = request.args.get("maxwidth", 800)
        if not photo_ref:
            return jsonify({"error": "photo_reference required"}), 400

        maps_service = MapsService()
        # Cache key based on photo reference and requested width
        cache_key = f"photo::{photo_ref}::w{maxwidth}"

        cached = default_cache.get(cache_key)
        if cached:
            content_type, data = cached
            return Response(data, content_type=content_type)

        photo_url = maps_service.get_photo_url(photo_ref, maxwidth=int(maxwidth))

        # Stream the image bytes back to the client
        r = requests.get(photo_url, stream=True, timeout=10)
        if r.status_code != 200:
            # If proxy fetch fails, return the photo URL as a fallback so the client can retrieve it directly.
            return jsonify({"photo_url": photo_url}), 200

        data = r.content
        content_type = r.headers.get("Content-Type", "image/jpeg")
        # Cache image bytes (default TTL configured in cache_service)
        try:
            default_cache.set(cache_key, content_type, data)
        except Exception:
            # On any cache failure, continue silently and return the image
            pass

        return Response(data, content_type=content_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@maps_bp.route("/geocode", methods=["GET"])
def geocode_location():
    """Geocode a location name to coordinates"""
    try:
        address = request.args.get("address")

        if not address:
            return jsonify({"error": "Address required"}), 400

        maps_service = MapsService()
        coordinates = maps_service.geocode(address)

        if not coordinates:
            return jsonify({"error": "Location not found"}), 404

        return jsonify(coordinates), 200

    except Exception as e:
        print(f"Geocoding error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@maps_bp.route("/distance", methods=["GET"])
def get_distance():
    """Calculate distance between two locations"""
    try:
        origin = request.args.get("origin")
        destination = request.args.get("destination")

        if not all([origin, destination]):
            return jsonify({"error": "Origin and destination required"}), 400

        maps_service = MapsService()
        distance_info = maps_service.get_distance(origin, destination)

        if not distance_info:
            return jsonify({"error": "Could not calculate distance"}), 400

        return jsonify(distance_info), 200

    except Exception as e:
        print(f"Distance calculation error: {str(e)}")
        return jsonify({"error": str(e)}), 500


