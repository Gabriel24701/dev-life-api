from conftest import _auth_headers, _register_and_login
from datetime import datetime, timedelta, timezone
import pytest


@pytest.fixture()
def two_users_with_goal(client):
    """Usuário A e B registrados/logados; A já tem uma goal criada."""
    token_a = _register_and_login(client, "a@example.com")
    token_b = _register_and_login(client, "b@example.com")
    target = (datetime.now(timezone.utc) + timedelta(days=15)).isoformat()
    goal = client.post(
        "/goals/", json={"title": "Meta da Ana", "target_date": target}, headers=_auth_headers(token_a)
    ).json()
    return token_a, token_b, goal


# ─── B tentando agir sobre goal de A ─────────────────────────────────────────
def test_get_goals_como_outro_usuario_nao_lista_goal_alheia(client, two_users_with_goal):
    _, token_b, _ = two_users_with_goal

    response = client.get("/goals/", headers=_auth_headers(token_b))

    assert response.status_code == 200
    assert response.json() == []


def test_update_goal_de_outro_usuario_retorna_404(client, two_users_with_goal):
    _, token_b, goal = two_users_with_goal

    response = client.put(
        f"/goals/{goal['id']}", json={"title": "Hackeado"}, headers=_auth_headers(token_b)
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Meta não encontrada ou não pertence a você"


def test_complete_goal_de_outro_usuario_retorna_404(client, two_users_with_goal):
    _, token_b, goal = two_users_with_goal

    response = client.put(f"/goals/{goal['id']}/complete", headers=_auth_headers(token_b))

    assert response.status_code == 404
    assert response.json()["detail"] == "Meta não encontrada ou não pertence a você"


def test_delete_goal_de_outro_usuario_retorna_404(client, two_users_with_goal):
    token_a, token_b, goal = two_users_with_goal

    response = client.delete(f"/goals/{goal['id']}", headers=_auth_headers(token_b))

    assert response.status_code == 404
    assert response.json()["detail"] == "Meta não encontrada ou não pertence a você"

    # sanity: a tentativa de B não afetou a goal de A
    still_there = client.get("/goals/", headers=_auth_headers(token_a)).json()
    assert len(still_there) == 1
    assert still_there[0]["id"] == goal["id"]


# ─── A (dono) age normalmente sobre a própria goal ──────────────────────────
def test_dono_consegue_editar_completar_e_deletar_a_propria_goal(client, two_users_with_goal):
    token_a, _, goal = two_users_with_goal

    update_response = client.put(
        f"/goals/{goal['id']}", json={"title": "Editado por A"}, headers=_auth_headers(token_a)
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Editado por A"

    complete_response = client.put(f"/goals/{goal['id']}/complete", headers=_auth_headers(token_a))
    assert complete_response.status_code == 200
    assert complete_response.json()["is_completed"] is True

    delete_response = client.delete(f"/goals/{goal['id']}", headers=_auth_headers(token_a))
    assert delete_response.status_code == 204

    remaining = client.get("/goals/", headers=_auth_headers(token_a)).json()
    assert remaining == []
