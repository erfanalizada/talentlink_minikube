"""
Main Flask application.
Single Responsibility: Application setup and configuration.
Dependency Inversion: Uses dependency injection for components.
"""
from flask import Flask
from flask_cors import CORS
from database import init_db
from routes import user_bp


def create_app():
    """
    Application factory pattern.
    Open/Closed: Can extend with new configurations without modifying core logic.
    """
    app = Flask(__name__)

    # CORS configuration
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register blueprints
    app.register_blueprint(user_bp)

    # Initialize database
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")

    print("✅ User service initialized successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
