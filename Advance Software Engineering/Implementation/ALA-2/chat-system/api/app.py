import json, os, time
import pika, redis
from flask import Flask, request, jsonify

app = Flask(__name__)

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
QUEUE = "chat_messages"

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


def publish(msg: dict):
    """Send one message to the RabbitMQ queue (persistent)."""
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.basic_publish(exchange="", routing_key=QUEUE, body=json.dumps(msg),
                     properties=pika.BasicProperties(delivery_mode=2))
    conn.close()


@app.post("/messages")
def post_message():
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("user") or not data.get("text"):
        return jsonify(error="'user' and 'text' are required"), 400
    msg = {"user": data["user"], "text": data["text"], "ts": time.time()}
    try:
        publish(msg)
    except pika.exceptions.AMQPError:
        return jsonify(error="message broker unavailable"), 503
    return jsonify(status="queued"), 202


@app.get("/messages")
def get_messages():
    items = [json.loads(x) for x in r.lrange("chat_history", -50, -1)]
    return jsonify(items)


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
