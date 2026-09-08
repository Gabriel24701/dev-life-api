from conftest import _auth_headers, _register_and_login
import pytest


@pytest.fixture()
def two_users_with_habit(client):
    """Usuário A e B registrados/logados; A já tem um hábito criado."""
    token_a = _register_and_login(client, "a@example.com")
    token_b = _register_and_login(client, "b@example.com")
    habit = client.post(
        "/habits/", json={"title": "Hábito da Ana"}, headers=_auth_headers(token_a)
    ).json()
    return token_a, token_b, habit


# ─── B tentando agir sobre hábito de A ───────────────────────────────────────
def test_get_habits_como_outro_usuario_nao_lista_habito_alheio(client, two_users_with_habit):
    _, token_b, _ = two_users_with_habit

    response = client.get("/habits/", headers=_auth_headers(token_b))

    assert response.status_code == 200
    assert response.json() == []


def test_update_habit_de_outro_usuario_retorna_404(client, two_users_with_habit):
    _, token_b, habit = two_users_with_habit

    response = client.put(
        f"/habits/{habit['id']}", json={"title": "Hackeado"}, headers=_auth_headers(token_b)
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Hábito não encontrado ou não pertence a você"


def test_increment_streak_de_outro_usuario_retorna_404(client, two_users_with_habit):
    _, token_b, habit = two_users_with_habit

    response = client.put(f"/habits/{habit['id']}/increment", headers=_auth_headers(token_b))

    assert response.status_code == 404
    assert response.json()["detail"] == "Hábito não encontrado ou não pertence a você"


def test_delete_habit_de_outro_usuario_retorna_404(client, two_users_with_habit):
    token_a, token_b, habit = two_users_with_habit

    response = client.delete(f"/habits/{habit['id']}", headers=_auth_headers(token_b))

    assert response.status_code == 404
    assert response.json()["detail"] == "Hábito não encontrado ou não pertence a você"

    # sanity: a tentativa de B não afetou o hábito de A
    still_there = client.get("/habits/", headers=_auth_headers(token_a)).json()
    assert len(still_there) == 1
    assert still_there[0]["id"] == habit["id"]


# ─── A (dono) age normalmente sobre o próprio hábito ────────────────────────
def test_dono_consegue_editar_incrementar_e_deletar_o_proprio_habito(client, two_users_with_habit):
    token_a, _, habit = two_users_with_habit

    update_response = client.put(
        f"/habits/{habit['id']}", json={"title": "Editado por A"}, headers=_auth_headers(token_a)
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Editado por A"

    increment_response = client.put(f"/habits/{habit['id']}/increment", headers=_auth_headers(token_a))
    assert increment_response.status_code == 200
    assert increment_response.json()["streak"] == 1

    delete_response = client.delete(f"/habits/{habit['id']}", headers=_auth_headers(token_a))
    assert delete_response.status_code == 204

    remaining = client.get("/habits/", headers=_auth_headers(token_a)).json()
    assert remaining == []
