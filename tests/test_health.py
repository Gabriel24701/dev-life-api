def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "checks": {"database": "ok"}}


def test_health_banco_indisponivel_retorna_503(client, db, monkeypatch):
    def _raise(*args, **kwargs):
        raise Exception("connection refused")

    monkeypatch.setattr(db, "execute", _raise)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "checks": {"database": "unavailable"}}
