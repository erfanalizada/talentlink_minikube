from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/jobs")
def list_jobs():
    return jsonify([
        {"id": 1, "title": "Internship (hardcoded)"},
        {"id": 2, "title": "Software Engineer (hardcoded)"}
    ])

@app.route("/api/jobs/health")
def health():
    return {"status": "job-service ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
