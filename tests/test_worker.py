import json

import worker
from worker import drain_queue, handle_user_created_event


def test_handle_user_created_event_parseia_e_loga(caplog):
    body = json.dumps(
        {
            "event": "user_created",
            "user_id": 42,
            "email": "worker-test@example.com",
            "auth_provider": "local",
            "created_at": "2026-09-13T00:00:00+00:00",
        }
    ).encode("utf-8")

    with caplog.at_level("INFO"):
        result = handle_user_created_event(body)

    assert result["user_id"] == 42
    assert result["email"] == "worker-test@example.com"
    assert "usuario criado" in caplog.text
    assert "worker-test@example.com" in caplog.text


class _FakeMethod:
    def __init__(self, delivery_tag):
        self.delivery_tag = delivery_tag


class _FakeChannel:
    """Channel fake pra testar drain_queue sem pika real: basic_get()
    devolve mensagens de uma fila em memoria e depois (None, None, None),
    igual pika quando a fila esvazia. basic_ack/basic_nack so registram o
    delivery_tag recebido, pra dar pra assertar o comportamento."""

    def __init__(self, bodies):
        self._bodies = list(bodies)
        self._next_tag = 1
        self.acked = []
        self.nacked = []

    def basic_get(self, queue, auto_ack=False):
        if not self._bodies:
            return None, None, None
        body = self._bodies.pop(0)
        tag = self._next_tag
        self._next_tag += 1
        return _FakeMethod(tag), None, body

    def basic_ack(self, delivery_tag):
        self.acked.append(delivery_tag)

    def basic_nack(self, delivery_tag, requeue=False):
        self.nacked.append(delivery_tag)


def _body(user_id):
    return json.dumps(
        {
            "user_id": user_id,
            "email": f"user{user_id}@example.com",
            "auth_provider": "local",
            "created_at": "2026-09-13T00:00:00+00:00",
        }
    ).encode("utf-8")


def test_drain_queue_processa_tudo_ate_fila_vazia():
    channel = _FakeChannel([_body(1), _body(2)])

    processed = drain_queue(channel)

    assert processed == 2
    assert channel.acked == [1, 2]
    assert channel.nacked == []


def test_drain_queue_respeita_limite_de_mensagens_por_execucao(monkeypatch):
    monkeypatch.setattr(worker, "MAX_MESSAGES_PER_RUN", 2)
    channel = _FakeChannel([_body(i) for i in range(5)])

    processed = drain_queue(channel)

    assert processed == 2
    assert channel.acked == [1, 2]
    # ainda sobraram mensagens na fila fake — confirma que parou antes de
    # esvaziar, deixando o resto para a proxima execucao do Cron.
    assert len(channel._bodies) == 3


def test_drain_queue_mensagem_invalida_nao_interrompe_as_seguintes():
    channel = _FakeChannel([b"isto nao e json valido", _body(9)])

    processed = drain_queue(channel)

    assert processed == 2
    assert channel.nacked == [1]
    assert channel.acked == [2]
