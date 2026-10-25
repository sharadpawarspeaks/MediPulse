import os
import logging
from flask import Flask, jsonify, render_template, request
from app.config import Config

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )
    app.config.from_object(config_class)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger("MediPulse")
    logger.info("Initializing MediPulse Health Intelligence Platform")

    # Register blueprints
    from app.routes.web_routes import web_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource or endpoint not found."}), 404
        return render_template("offline.html", error_message="Page Not Found (404)"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}")
        if request.path.startswith("/api/"):
            return jsonify({"error": "An internal server error occurred. Please try again."}), 500
        return render_template("offline.html", error_message="Internal Server Error (500)"), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"error": "Uploaded payload or file exceeds maximum allowed limit (6MB)."}), 413

    return app
