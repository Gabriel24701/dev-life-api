from conftest import _auth_headers, _register_and_login
import pytest


@pytest.fixture()
def two_users_with_task(client):
    """Usuário A e B registrados/logados; A já tem uma task criada."""
    token_a = _register_and_login(client, "a@example.com")
    token_b = _register_and_login(client, "b@example.com")
    task = client.post(
        "/tasks/", json={"title": "Task da Ana"}, headers=_auth_headers(token_a)
    ).json()
    return token_a, token_b, task


# ─── B tentando agir sobre task de A ────────────────────────────────────────
def test_get_tasks_como_outro_usuario_nao_lista_task_alheia(client, two_users_with_task):
    _, token_b, _ = two_users_with_task

    response = client.get("/tasks/", headers=_auth_headers(token_b))

    assert response.status_code == 200
    assert response.json() == []


def test_update_task_de_outro_usuario_retorna_404(client, two_users_with_task):
    _, token_b, task = two_users_with_task

    response = client.put(
        f"/tasks/{task['id']}", json={"title": "Hackeado"}, headers=_auth_headers(token_b)
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa não encontrada ou não pertence a você"


def test_complete_task_de_outro_usuario_retorna_404(client, two_users_with_task):
    _, token_b, task = two_users_with_task

    response = client.put(f"/tasks/{task['id']}/complete", headers=_auth_headers(token_b))

    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa não encontrada ou não pertence a você"


def test_delete_task_de_outro_usuario_retorna_404(client, two_users_with_task):
    token_a, token_b, task = two_users_with_task

    response = client.delete(f"/tasks/{task['id']}", headers=_auth_headers(token_b))

    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa não encontrada ou não pertence a você"

    # sanity: a tentativa de B não afetou a task de A
    still_there = client.get("/tasks/", headers=_auth_headers(token_a)).json()
    assert len(still_there) == 1
    assert still_there[0]["id"] == task["id"]


# ─── A (dono) age normalmente sobre a própria task ──────────────────────────
def test_dono_consegue_editar_completar_e_deletar_a_propria_task(client, two_users_with_task):
    token_a, _, task = two_users_with_task

    update_response = client.put(
        f"/tasks/{task['id']}", json={"title": "Editado por A"}, headers=_auth_headers(token_a)
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Editado por A"

    complete_response = client.put(f"/tasks/{task['id']}/complete", headers=_auth_headers(token_a))
    assert complete_response.status_code == 200
    assert complete_response.json()["is_completed"] is True

    delete_response = client.delete(f"/tasks/{task['id']}", headers=_auth_headers(token_a))
    assert delete_response.status_code == 204

    remaining = client.get("/tasks/", headers=_auth_headers(token_a)).json()
    assert remaining == []
