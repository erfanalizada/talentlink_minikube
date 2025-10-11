from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/notifications/send", methods=["POST"])
def send_notification():
    return jsonify({"message": "Notification sent (hardcoded)"})

@app.route("/api/notifications/health")
def health():
    return {"status": "notification-service ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
