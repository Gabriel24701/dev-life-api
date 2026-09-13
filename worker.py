import json
import logging

import pika

from messaging.publisher import EXCHANGE_NAME, RABBITMQ_URL, USER_CREATED_ROUTING_KEY

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)

QUEUE_NAME = "dev_life.user_created"


def handle_user_created_event(body: bytes) -> dict:
    """Trata uma mensagem 'user_created': parseia o payload e loga de forma
    estruturada. Nao faz ack/nack (fica no callback do consumer) — so
    transforma bytes -> dict e loga, por isso e testavel sem broker real.
    """
    payload = json.loads(body)
    logger.info(
        "usuario criado | user_id=%s email=%s auth_provider=%s created_at=%s",
        payload.get("user_id"),
        payload.get("email"),
        payload.get("auth_provider"),
        payload.get("created_at"),
    )
    return payload


def _on_message(channel, method, properties, body):
    try:
        handle_user_created_event(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.error("Falha ao processar mensagem user_created", exc_info=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    if not RABBITMQ_URL:
        raise SystemExit("RABBITMQ_URL nao configurada — worker precisa de uma fila real.")

    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(
        exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=USER_CREATED_ROUTING_KEY
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=_on_message)

    logger.info("Worker aguardando eventos user_created em '%s'...", QUEUE_NAME)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
