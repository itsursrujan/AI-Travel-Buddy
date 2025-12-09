# backend/main.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config, config_by_name
from database import MongoDatabase
from routes.auth_routes import auth_bp
from routes.itinerary_routes import itinerary_bp
from routes.analytics_routes import analytics_bp
from routes.maps_routes import maps_bp
from routes.bigquery_routes import bigquery_bp
from routes.image_routes import image_bp
from services.bigquery_service import BigQueryService

def create_app(config_name="development"):
    """Application factory"""
    app = Flask(__name__)
    
    # Load config
    config_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})
    
    # Connect to database
    with app.app_context():
        MongoDatabase.connect()
    
    # Initialize BigQuery and create tables
    print("\n" + "="*60)
    print("Initializing BigQuery...")
    print("="*60)
    try:
        bq_service = BigQueryService()
        if bq_service.client:
            bq_service.create_tables()
            print("✓ BigQuery initialization complete")
        else:
            print("⚠ BigQuery client not available - analytics may not work")
    except Exception as e:
        print(f"⚠ BigQuery initialization error: {str(e)}")
    print("="*60 + "\n")
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(itinerary_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(maps_bp)
    app.register_blueprint(bigquery_bp)
    app.register_blueprint(image_bp)
    
    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy", "service": "AI Travel Buddy Backend"}), 200
    
    # Root endpoint
    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "service": "AI Travel Buddy Backend",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth",
                "itinerary": "/api/itinerary",
                "analytics": "/api/analytics",
                "maps": "/api/maps",
                "bigquery": "/api/analytics (BigQuery endpoints)"
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app

if __name__ == "__main__":
    app = create_app("development")
    # Disable debug mode to avoid Windows socket issues
    app.run(debug=False, host="0.0.0.0", port=8000, use_reloader=False)


