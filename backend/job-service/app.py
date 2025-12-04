"""
Job Service - Main application entry point.
Handles job postings and applications.
"""
from flask import Flask
from flask_cors import CORS
from database import init_db
from routes import jobs_bp

app = Flask(__name__)
# Enable CORS for frontend communication. Explicitly allow the frontend origin
# and the cluster host so Access-Control-Allow-Credentials can be used safely.
CORS(app,
    resources={r"/api/*": {"origins": ["http://localhost:3000", "http://talentlink.local"]}},
    supports_credentials=True)

# Register blueprints
app.register_blueprint(jobs_bp)

# Initialize database on startup
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
