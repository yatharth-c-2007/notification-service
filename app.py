"""
notification-service
Simulates dispatching a notification (email/SMS/push) for an order
event. Doesn't actually send anything external — logs the event
and returns an acknowledgement. Keeps a small in-memory history so
we have something real to inspect/observe later.
"""
from flask import Flask, jsonify, request
import os
import logging
import threading
from datetime import datetime, timezone

app = Flask(__name__)
lock = threading.Lock()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")

HISTORY = []  # list of dicts, most recent last
MAX_HISTORY = 100


@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", service="notification-service"), 200


@app.route("/notify", methods=["POST"])
def notify():
    body = request.get_json(silent=True) or {}

    order_id = body.get("order_id")
    channel = body.get("channel", "email")
    message = body.get("message", "")

    if not order_id:
        return jsonify(error="order_id is required"), 400

    event = {
        "order_id": order_id,
        "channel": channel,
        "message": message,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info("Notification dispatched: %s", event)

    with lock:
        HISTORY.append(event)
        if len(HISTORY) > MAX_HISTORY:
            HISTORY.pop(0)

    return jsonify(status="sent", **event), 200


@app.route("/notifications", methods=["GET"])
def list_notifications():
    with lock:
        return jsonify(notifications=list(HISTORY)), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port)
