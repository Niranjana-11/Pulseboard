import os
import psycopg2
import pika
import redis
from dotenv import load_dotenv

load_dotenv()


def check_postgres():
    conn = psycopg2.connect(
        host="localhost",
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        print("  Postgres version:", cur.fetchone()[0])
    conn.close()


def check_rabbitmq():
    creds = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER"), os.getenv("RABBITMQ_PASSWORD")
    )
    params = pika.ConnectionParameters(
        host="localhost",
        port=int(os.getenv("RABBITMQ_PORT", 5672)),
        credentials=creds,
    )
    conn = pika.BlockingConnection(params)
    channel = conn.channel()
    channel.queue_declare(queue="healthcheck")

    # Mini producer -> queue -> consumer demo
    channel.basic_publish(exchange="", routing_key="healthcheck", body=b"hello queue")
    method, _, body = channel.basic_get(queue="healthcheck", auto_ack=True)
    print("  Message round trip:", body.decode() if body else "NO MESSAGE")

    channel.queue_delete(queue="healthcheck")
    conn.close()


def check_redis():
    r = redis.Redis(host="localhost", port=int(os.getenv("REDIS_PORT", 6379)))
    r.set("pulseboard:ping", "pong", ex=30)
    print("  Redis value:", r.get("pulseboard:ping").decode())


if __name__ == "__main__":
    for name, fn in [
        ("PostgreSQL", check_postgres),
        ("RabbitMQ", check_rabbitmq),
        ("Redis", check_redis),
    ]:
        try:
            print(f"[{name}]")
            fn()
            print("  -> OK\n")
        except Exception as e:
            print(f"  -> FAILED: {e}\n")