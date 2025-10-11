from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/matching/search")
def search():
    return jsonify({
        "job_id": 1,
        "candidates": [
            {"id": 101, "name": "Alice"},
            {"id": 102, "name": "Bob"}
        ]
    })

@app.route("/api/matching/health")
def health():
    return {"status": "matching-service ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
