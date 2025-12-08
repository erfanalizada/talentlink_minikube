"""
Notification Service - Handles sending email notifications.
Subscribes to RabbitMQ events and sends emails when triggered.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import os
import time
from dotenv import load_dotenv
from event_consumer import EventConsumer
from email_sender import EmailSender

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize email sender
email_sender = EmailSender()

# Global event consumer instance
event_consumer = None
consumer_thread = None


def start_event_consumer():
    """
    Start RabbitMQ event consumer in a separate thread.
    This runs continuously, listening for events.
    """
    global event_consumer

    # Wait for RabbitMQ to be ready
    print("⏳ Waiting 10 seconds for RabbitMQ to be ready...")
    time.sleep(10)

    print("🚀 Starting RabbitMQ event consumer thread...")
    event_consumer = EventConsumer()
    event_consumer.start_consuming()


@app.route("/api/notifications/send", methods=["POST"])
def send_notification():
    """
    Manual endpoint to send notifications (for testing).
    """
    try:
        data = request.get_json()
        notification_type = data.get('type')
        recipient_email = data.get('email')
        recipient_name = data.get('name', 'User')

        if not recipient_email:
            return jsonify({"error": "email is required"}), 400

        if notification_type == 'application_accepted':
            job_title = data.get('job_title')
            success = email_sender.send_application_accepted_email(
                employee_email=recipient_email,
                employee_username=recipient_name,
                job_title=job_title
            )
            return jsonify({"success": success}), 200 if success else 500

        return jsonify({"error": "Unknown notification type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/notifications/health")
def health():
    """Health check endpoint."""
    consumer_status = "running" if event_consumer and event_consumer.connection and not event_consumer.connection.is_closed else "not connected"

    return jsonify({
        "status": "notification-service ok",
        "rabbitmq_consumer": consumer_status
    }), 200


@app.route("/api/notifications/stats")
def stats():
    """Statistics endpoint."""
    return jsonify({
        "service": "notification-service",
        "version": "1.0.0",
        "features": [
            "Email notifications",
            "RabbitMQ event consumer",
            "ApplicationAccepted event handling"
        ],
        "consumer_active": event_consumer is not None
    }), 200


if __name__ == "__main__":
    # Start event consumer in background thread
    consumer_thread = threading.Thread(target=start_event_consumer, daemon=True)
    consumer_thread.start()
    print("✅ Event consumer thread started")

    # Start Flask app
    print("🚀 Starting Flask app on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)
