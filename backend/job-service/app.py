"""
Job Service - Main application entry point.
Handles job postings and applications.
"""
from flask import Flask
from flask_cors import CORS
from database import init_db
from routes import jobs_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Register blueprints
app.register_blueprint(jobs_bp)

# Initialize database on startup
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
