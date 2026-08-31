# ─── create_habit ────────────────────────────────────────────────────────────
def test_create_habit_com_description_persiste_corretamente(client, auth_headers):
    response = client.post(
        "/habits/", json={"title": "H1", "description": "desc H1"}, headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["description"] == "desc H1"


def test_create_habit_sem_description_fica_null(client, auth_headers):
    response = client.post("/habits/", json={"title": "H2"}, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["description"] is None


# ─── update_habit (partial) ─────────────────────────────────────────────────
def test_update_habit_so_title_mantem_description_inalterada(client, auth_headers):
    created = client.post("/habits/", json={"title": "H3"}, headers=auth_headers).json()
    assert created["description"] is None

    response = client.put(
        f"/habits/{created['id']}", json={"title": "H3 renomeado"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "H3 renomeado"
    assert body["description"] is None


def test_update_habit_so_description_mantem_title_inalterado(client, auth_headers):
    created = client.post(
        "/habits/", json={"title": "H4", "description": "desc original"}, headers=auth_headers
    ).json()

    response = client.put(
        f"/habits/{created['id']}", json={"description": "desc nova"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "H4"
    assert body["description"] == "desc nova"
