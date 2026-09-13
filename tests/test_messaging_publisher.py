import logging

from messaging import publisher


def test_publish_sem_rabbitmq_url_nao_tenta_conectar(monkeypatch, caplog):
    monkeypatch.setattr(publisher, "RABBITMQ_URL", None)

    def _fail_if_called(*args, **kwargs):
        raise AssertionError("BlockingConnection nao deveria ser chamado sem RABBITMQ_URL")

    monkeypatch.setattr(publisher.pika, "BlockingConnection", _fail_if_called)

    with caplog.at_level(logging.INFO):
        publisher.publish_user_created(user_id=1, email="sem-url@example.com")

    assert "nao publicado" in caplog.text


def test_publish_falha_de_conexao_nao_propaga(monkeypatch, caplog):
    monkeypatch.setattr(publisher, "RABBITMQ_URL", "amqps://user:pass@host/vhost")

    def _raise(*args, **kwargs):
        raise ConnectionError("broker fora do ar")

    monkeypatch.setattr(publisher.pika, "BlockingConnection", _raise)

    with caplog.at_level(logging.ERROR):
        publisher.publish_user_created(user_id=2, email="falha@example.com")

    assert "Falha ao publicar evento user_created" in caplog.text
