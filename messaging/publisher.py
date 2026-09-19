import json
import logging
import os
from datetime import datetime, timezone

import pika

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

EXCHANGE_NAME = "dev_life.events"
USER_CREATED_ROUTING_KEY = "user.created"


def publish_user_created(user_id: int, email: str, auth_provider: str = "local") -> None:
    """Publica o evento 'usuario criado' no RabbitMQ.

    Nunca propaga excecao: falha de mensageria (fila fora do ar, timeout,
    credencial invalida) nao deve derrubar o fluxo de registro que chamou
    esta funcao. Em caso de falha, loga em nivel error com contexto:
    nao-bloqueante, mas nao silencioso.
    """
    if not RABBITMQ_URL:
        logger.info(
            "RABBITMQ_URL nao configurada — evento user_created nao publicado (user_id=%s)",
            user_id,
        )
        return

    payload = {
        "event": "user_created",
        "user_id": user_id,
        "email": email,
        "auth_provider": auth_provider,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    connection = None
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        params.connection_attempts = 1
        params.socket_timeout = 5
        params.blocked_connection_timeout = 5

        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(
            exchange=EXCHANGE_NAME, exchange_type="topic", durable=True
        )
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=USER_CREATED_ROUTING_KEY,
            body=json.dumps(payload).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json", delivery_mode=2
            ),
        )
        logger.info("Evento user_created publicado (user_id=%s)", user_id)
    except Exception:
        logger.error(
            "Falha ao publicar evento user_created (user_id=%s) — registro segue normalmente",
            user_id,
            exc_info=True,
        )
    finally:
        if connection is not None and connection.is_open:
            try:
                connection.close()
            except Exception:
                logger.warning("Falha ao fechar conexao RabbitMQ apos publish", exc_info=True)
