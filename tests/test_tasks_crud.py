# ─── create_task ─────────────────────────────────────────────────────────────
def test_create_task_com_priority_valido_persiste_corretamente(client, auth_headers):
    response = client.post("/tasks/", json={"title": "T1", "priority": "high"}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["priority"] == "high"


def test_create_task_com_priority_invalido_retorna_422(client, auth_headers):
    response = client.post("/tasks/", json={"title": "T2", "priority": "urgent"}, headers=auth_headers)

    assert response.status_code == 422


def test_create_task_sem_priority_aplica_default_medium(client, auth_headers):
    response = client.post("/tasks/", json={"title": "T3"}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_create_task_com_tags_persiste_corretamente(client, auth_headers):
    response = client.post(
        "/tasks/", json={"title": "T4", "tags": "backend,urgente"}, headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["tags"] == "backend,urgente"


# ─── update_task (partial) ──────────────────────────────────────────────────
def test_update_task_so_title_mantem_demais_campos_inalterados(client, auth_headers):
    created = client.post(
        "/tasks/",
        json={"title": "T4", "description": "desc original", "priority": "low", "tags": "x,y"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/tasks/{created['id']}", json={"title": "T4 renomeada"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "T4 renomeada"
    assert body["description"] == "desc original"
    assert body["priority"] == "low"
    assert body["tags"] == "x,y"


def test_update_task_com_priority_invalido_retorna_422(client, auth_headers):
    created = client.post("/tasks/", json={"title": "T5"}, headers=auth_headers).json()

    response = client.put(
        f"/tasks/{created['id']}", json={"priority": "urgent"}, headers=auth_headers
    )

    assert response.status_code == 422


# ─── complete_task (toggle) ─────────────────────────────────────────────────
def test_complete_task_alterna_de_false_para_true(client, auth_headers):
    created = client.post("/tasks/", json={"title": "T6"}, headers=auth_headers).json()
    assert created["is_completed"] is False

    response = client.put(f"/tasks/{created['id']}/complete", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["is_completed"] is True


def test_complete_task_chamado_de_novo_volta_para_false(client, auth_headers):
    """Guarda contra regressão do bug de toggle 'sempre true': a segunda
    chamada precisa desmarcar a tarefa, não mantê-la concluída."""
    created = client.post("/tasks/", json={"title": "T7"}, headers=auth_headers).json()
    client.put(f"/tasks/{created['id']}/complete", headers=auth_headers)  # False -> True

    response = client.put(f"/tasks/{created['id']}/complete", headers=auth_headers)  # True -> False

    assert response.status_code == 200
    assert response.json()["is_completed"] is False
