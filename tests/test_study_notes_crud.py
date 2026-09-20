# ─── create_study_note ───────────────────────────────────────────────────────
def test_create_study_note_com_tags_persiste_corretamente(client, auth_headers):
    response = client.post(
        "/study-notes/",
        json={"title": "SOLID", "content": "Resumo dos 5 princípios", "tags": "poo,arquitetura"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "SOLID"
    assert body["content"] == "Resumo dos 5 princípios"
    assert body["tags"] == "poo,arquitetura"


def test_create_study_note_sem_tags_aplica_none(client, auth_headers):
    response = client.post(
        "/study-notes/",
        json={"title": "Terraform", "content": "Anotações do curso"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["tags"] is None


def test_create_study_note_sem_content_retorna_422(client, auth_headers):
    response = client.post("/study-notes/", json={"title": "Nota incompleta"}, headers=auth_headers)

    assert response.status_code == 422


# ─── update_study_note (partial) ────────────────────────────────────────────
def test_update_study_note_so_title_mantem_content_e_tags_inalterados(client, auth_headers):
    created = client.post(
        "/study-notes/",
        json={"title": "Original", "content": "conteúdo original", "tags": "x,y"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/study-notes/{created['id']}", json={"title": "Renomeada"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Renomeada"
    assert body["content"] == "conteúdo original"
    assert body["tags"] == "x,y"


def test_update_study_note_so_content_mantem_title_e_tags_inalterados(client, auth_headers):
    created = client.post(
        "/study-notes/",
        json={"title": "Título fixo", "content": "conteúdo original", "tags": "x,y"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/study-notes/{created['id']}", json={"content": "conteúdo editado"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Título fixo"
    assert body["content"] == "conteúdo editado"
    assert body["tags"] == "x,y"


def test_update_study_note_so_tags_mantem_title_e_content_inalterados(client, auth_headers):
    created = client.post(
        "/study-notes/",
        json={"title": "Título fixo", "content": "conteúdo fixo", "tags": "antiga"},
        headers=auth_headers,
    ).json()

    response = client.put(
        f"/study-notes/{created['id']}", json={"tags": "nova,tag"}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Título fixo"
    assert body["content"] == "conteúdo fixo"
    assert body["tags"] == "nova,tag"
