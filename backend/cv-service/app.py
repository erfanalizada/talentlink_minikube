from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/cv/upload", methods=["POST"])
def upload_cv():
    return jsonify({"message": "CV uploaded (hardcoded)", "status": "ok"})

@app.route("/api/cv/health")
def health():
    return {"status": "cv-service ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
