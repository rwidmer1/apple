from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import time
import uuid

app = Flask(__name__)
CORS(app)

# Messages en attente par client_id
pending_messages = {}
# Pages HTML stockées par message_id
message_pages = {}

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
    background: #f5f5f7;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }
  .card {
    background: white;
    border-radius: 18px;
    box-shadow: 0 4px 40px rgba(0,0,0,0.12);
    padding: 2.5rem;
    max-width: 680px;
    width: 100%;
  }
  .header { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #999; margin-bottom: 0.5rem; }
  h1 { font-size: 1.6rem; font-weight: 700; color: #1d1d1f; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #e5e5e5; }
  .content { line-height: 1.7; color: #333; font-size: 1rem; }
  .content img { max-width: 100%; border-radius: 10px; margin: 1rem 0; }
  .content a { color: #0071e3; }
  .content h2 { margin: 1rem 0 0.5rem; }
  .content p { margin-bottom: 0.75rem; }
  .buttons { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1.75rem; }
  .btn {
    display: inline-block;
    background: #0071e3;
    color: white;
    text-decoration: none;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    transition: background 0.2s, transform 0.1s;
  }
  .btn:hover { background: #0077ed; transform: scale(1.02); }
  .btn:active { transform: scale(0.98); }
  .footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e5e5; font-size: 0.75rem; color: #aaa; text-align: right; }
</style>
</head>
<body>
<div class="card">
  <div class="header">Alerte détectée</div>
  <h1>{{ title }}</h1>
  <div class="content">{{ html_content }}</div>
  {% if buttons %}
  <div class="buttons">
    {% for btn in buttons %}
    <a href="{{ btn.url }}" target="_blank" class="btn">{{ btn.label }}</a>
    {% endfor %}
  </div>
  {% endif %}
  <div class="footer">{{ sent_at }}</div>
</div>
</body>
</html>"""

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    client_id = data.get("client_id", "default")
    title = data.get("title", "Message")
    html_content = data.get("html_content", "")
    message = data.get("message", "")
    buttons = data.get("buttons", [])

    if not html_content and not message:
        return jsonify({"error": "Contenu vide"}), 400

    msg_id = str(uuid.uuid4())[:8]
    sent_at = time.strftime("%d/%m/%Y à %H:%M")

    message_pages[msg_id] = {
        "title": title,
        "html_content": html_content or f"<p>{message}</p>",
        "buttons": [b for b in buttons if b.get("label") and b.get("url")],
        "sent_at": sent_at
    }

    if client_id not in pending_messages:
        pending_messages[client_id] = []

    pending_messages[client_id].append({
        "title": title,
        "message": message or "Vous avez reçu un message.",
        "msg_id": msg_id,
        "timestamp": time.time()
    })

    return jsonify({"status": "ok", "msg_id": msg_id})

@app.route("/message/<msg_id>", methods=["GET"])
def view_message(msg_id):
    page = message_pages.get(msg_id)
    if not page:
        return "Message introuvable.", 404
    return render_template_string(PAGE_TEMPLATE, **page)

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
