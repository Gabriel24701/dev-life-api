from conftest import _auth_headers, _register_and_login
import pytest


@pytest.fixture()
def two_users_with_note(client):
    """Usuário A e B registrados/logados; A já tem uma nota criada."""
    token_a = _register_and_login(client, "a@example.com")
    token_b = _register_and_login(client, "b@example.com")
    note = client.post(
        "/study-notes/",
        json={"title": "Nota da Ana", "content": "conteúdo da Ana"},
        headers=_auth_headers(token_a),
    ).json()
    return token_a, token_b, note


# ─── B tentando agir sobre nota de A ─────────────────────────────────────────
def test_get_study_notes_como_outro_usuario_nao_lista_nota_alheia(client, two_users_with_note):
    _, token_b, _ = two_users_with_note

    response = client.get("/study-notes/", headers=_auth_headers(token_b))

    assert response.status_code == 200
    assert response.json() == []


def test_update_study_note_de_outro_usuario_retorna_404(client, two_users_with_note):
    _, token_b, note = two_users_with_note

    response = client.put(
        f"/study-notes/{note['id']}", json={"title": "Hackeado"}, headers=_auth_headers(token_b)
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Nota não encontrada ou não pertence a você"


def test_delete_study_note_de_outro_usuario_retorna_404(client, two_users_with_note):
    token_a, token_b, note = two_users_with_note

    response = client.delete(f"/study-notes/{note['id']}", headers=_auth_headers(token_b))

    assert response.status_code == 404
    assert response.json()["detail"] == "Nota não encontrada ou não pertence a você"

    # sanity: a tentativa de B não afetou a nota de A
    still_there = client.get("/study-notes/", headers=_auth_headers(token_a)).json()
    assert len(still_there) == 1
    assert still_there[0]["id"] == note["id"]


# ─── A (dono) age normalmente sobre a própria nota ──────────────────────────
def test_dono_consegue_editar_e_deletar_a_propria_nota(client, two_users_with_note):
    token_a, _, note = two_users_with_note

    update_response = client.put(
        f"/study-notes/{note['id']}", json={"title": "Editado por A"}, headers=_auth_headers(token_a)
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Editado por A"

    delete_response = client.delete(f"/study-notes/{note['id']}", headers=_auth_headers(token_a))
    assert delete_response.status_code == 204

    remaining = client.get("/study-notes/", headers=_auth_headers(token_a)).json()
    assert remaining == []
