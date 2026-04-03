from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Stockage en mémoire des messages en attente (par client_id)
pending_messages = {}

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    client_id = data.get("client_id", "default")
    message = data.get("message", "")
    title = data.get("title", "Message")

    if not message:
        return jsonify({"error": "Message vide"}), 400

    if client_id not in pending_messages:
        pending_messages[client_id] = []

    pending_messages[client_id].append({
        "title": title,
        "message": message,
        "timestamp": time.time()
    })

    return jsonify({"status": "ok", "queued": len(pending_messages[client_id])})

@app.route("/poll/<client_id>", methods=["GET"])
def poll(client_id):
    messages = pending_messages.get(client_id, [])
    if messages:
        pending_messages[client_id] = []
        return jsonify({"messages": messages})
    return jsonify({"messages": []})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "running", "clients": list(pending_messages.keys())})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
