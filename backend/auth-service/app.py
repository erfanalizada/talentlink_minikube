from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------- AUTH ENDPOINTS ----------------
@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    Mock login endpoint.
    Accepts JSON { "username": "user", "password": "pass" }
    Returns a fake token response.
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "guest")
    return jsonify({
        "message": f"User '{username}' logged in (mocked)",
        "token": "fake-jwt-token-123"
    })


@app.route("/api/auth/register", methods=["POST"])
def register():
    """
    Mock register endpoint.
    Accepts JSON { "username": ..., "email": ... }
    Returns a success message.
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "new_user")
    return jsonify({
        "message": f"User '{username}' registered successfully (mocked)"
    })


@app.route("/api/auth/health")
def health():
    """Health check endpoint for Kubernetes readiness/liveness probes."""
    return jsonify({"status": "auth-service ok"}), 200


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
