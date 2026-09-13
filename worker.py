import json
import logging
import os
import sys
import time

import pika

from messaging.publisher import EXCHANGE_NAME, RABBITMQ_URL, USER_CREATED_ROUTING_KEY

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger(__name__)

QUEUE_NAME = "dev_life.user_created"

# Limites de seguranca por execucao do Job — evita que um acumulo anormal
# de mensagens (ex.: RabbitMQ fora do ar por um dia) faca uma unica
# execucao rodar por tempo indefinido. O que sobrar fica pra proxima
# chamada do Cron.
MAX_MESSAGES_PER_RUN = int(os.getenv("WORKER_MAX_MESSAGES", "500"))
MAX_RUNTIME_SECONDS = float(os.getenv("WORKER_MAX_SECONDS", "60"))


def handle_user_created_event(body: bytes) -> dict:
    """Trata uma mensagem 'user_created': parseia o payload e loga de forma
    estruturada. Nao faz ack/nack (fica no chamador) — so transforma
    bytes -> dict e loga, por isso e testavel sem broker real.
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


def drain_queue(channel) -> int:
    """Consome QUEUE_NAME ate esvaziar ou ate um dos limites de seguranca
    ser atingido. Retorna quantas mensagens foram processadas (sucesso +
    falha individual) nesta execucao.

    Falha ao tratar UMA mensagem (ex.: JSON invalido) descarta so aquela
    mensagem (nack sem requeue) e segue pra proxima — nao interrompe o
    drain. Uma falha de conexao (ex.: broker cai no meio) nao e capturada
    aqui: propaga pra fora, porque isso e falha real de execucao, nao
    problema de uma mensagem so.
    """
    processed = 0
    start = time.monotonic()

    while processed < MAX_MESSAGES_PER_RUN:
        if time.monotonic() - start > MAX_RUNTIME_SECONDS:
            logger.warning(
                "Limite de tempo (%ss) atingido com %s mensagem(ns) processada(s) "
                "— restante fica para a proxima execucao",
                MAX_RUNTIME_SECONDS,
                processed,
            )
            break

        method, _properties, body = channel.basic_get(queue=QUEUE_NAME, auto_ack=False)
        if method is None:
            break  # fila vazia — drain concluido

        try:
            handle_user_created_event(body)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.error("Falha ao processar mensagem user_created", exc_info=True)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        processed += 1
    else:
        logger.warning(
            "Limite de %s mensagem(ns) por execucao atingido — restante fica "
            "para a proxima execucao",
            MAX_MESSAGES_PER_RUN,
        )

    return processed


def main() -> int:
    if not RABBITMQ_URL:
        logger.error("RABBITMQ_URL nao configurada — worker precisa de uma fila real.")
        return 1

    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(
            exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=USER_CREATED_ROUTING_KEY
        )
    except Exception:
        logger.error("Nao foi possivel conectar/configurar o RabbitMQ", exc_info=True)
        return 1

    try:
        processed = drain_queue(channel)
        logger.info("Drain concluido: %s mensagem(ns) processada(s)", processed)
        return 0
    except Exception:
        logger.error("Falha durante o drain — execucao do Job falhou", exc_info=True)
        return 1
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
