from datetime import datetime, timedelta, timezone


def _future_iso(days):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


# ─── create_goal ─────────────────────────────────────────────────────────────
def test_create_goal_com_target_date_persiste_corretamente(client, auth_headers):
    response = client.post(
        "/goals/",
        json={"title": "Aprender Terraform", "target_date": _future_iso(30)},
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Aprender Terraform"
    assert body["is_completed"] is False


def test_create_goal_sem_target_date_retorna_422(client, auth_headers):
    response = client.post("/goals/", json={"title": "Meta sem prazo"}, headers=auth_headers)

    assert response.status_code == 422


# ─── update_goal (partial) ──────────────────────────────────────────────────
def test_update_goal_so_title_mantem_target_date_inalterado(client, auth_headers):
    created = client.post(
        "/goals/", json={"title": "Meta original", "target_date": _future_iso(10)}, headers=auth_headers
    ).json()

    response = client.put(
        f"/goals/{created['id']}", json={"title": "Meta renomeada"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Meta renomeada"
    assert body["target_date"] == created["target_date"]


# ─── complete_goal (toggle) ─────────────────────────────────────────────────
def test_complete_goal_alterna_de_false_para_true(client, auth_headers):
    created = client.post(
        "/goals/", json={"title": "Meta a concluir", "target_date": _future_iso(5)}, headers=auth_headers
    ).json()
    assert created["is_completed"] is False

    response = client.put(f"/goals/{created['id']}/complete", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["is_completed"] is True


def test_complete_goal_chamado_de_novo_volta_para_false(client, auth_headers):
    """Guarda contra regressão do bug de toggle 'sempre true' (mesmo caso já
    corrigido em complete_task): a segunda chamada precisa desmarcar a meta,
    não mantê-la concluída."""
    created = client.post(
        "/goals/", json={"title": "Meta toggle", "target_date": _future_iso(5)}, headers=auth_headers
    ).json()
    client.put(f"/goals/{created['id']}/complete", headers=auth_headers)  # False -> True

    response = client.put(f"/goals/{created['id']}/complete", headers=auth_headers)  # True -> False

    assert response.status_code == 200
    assert response.json()["is_completed"] is False
