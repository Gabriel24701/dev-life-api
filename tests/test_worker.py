import json

from worker import handle_user_created_event


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
