import json, os, time, socket
import pika, redis

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
QUEUE = "chat_messages"
WORKER_ID = socket.gethostname()

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


def on_message(ch, method, properties, body):
    msg = json.loads(body)
    msg["processed_by"] = WORKER_ID  # shows which worker handled it
    r.rpush("chat_history", json.dumps(msg))
    print(f"[{WORKER_ID}] stored message from {msg['user']}", flush=True)
    ch.basic_ack(delivery_tag=method.delivery_tag)  # ack only after saving


def main():
    while True:  # retry until RabbitMQ is ready
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
            break
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not ready, retrying in 3s...", flush=True)
            time.sleep(3)
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.basic_qos(prefetch_count=1)  # fair dispatch between workers
    ch.basic_consume(queue=QUEUE, on_message_callback=on_message)
    print(f"[{WORKER_ID}] waiting for messages...", flush=True)
    ch.start_consuming()


if __name__ == "__main__":
    main()
