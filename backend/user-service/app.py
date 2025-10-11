from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/users/profile")
def profile():
    return jsonify({
        "id": 1,
        "name": "Hardcoded User",
        "email": "user@example.com"
    })

@app.route("/api/users/health")
def health():
    return {"status": "user-service ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
