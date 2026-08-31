from conftest import _auth_headers, _register_and_login
from models.models import User


# ─── POST /auth/register ────────────────────────────────────────────────────
def test_register_sucesso_retorna_201_sem_expor_hash(client):
    response = client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana@example.com", "password": "secret123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert body["name"] == "Ana"
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_email_duplicado_retorna_400(client):
    payload = {"name": "Ana", "email": "ana@example.com", "password": "secret123"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json={**payload, "name": "Ana 2"})

    assert response.status_code == 400
    assert response.json()["detail"] == "E-mail já cadastrado."


# ─── POST /auth/login ───────────────────────────────────────────────────────
def test_login_sucesso_retorna_token(client):
    client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana@example.com", "password": "secret123"},
    )
    response = client.post(
        "/auth/login", data={"username": "ana@example.com", "password": "secret123"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_senha_errada_retorna_401(client):
    client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana@example.com", "password": "secret123"},
    )

    response = client.post(
        "/auth/login", data={"username": "ana@example.com", "password": "senha-errada"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos"


def test_login_usuario_inexistente_retorna_401_com_mesma_mensagem_da_senha_errada(client):
    # Confirmado manualmente: mesmo status e mesma mensagem que senha errada —
    # o endpoint não vaza quais e-mails estão cadastrados.
    response = client.post(
        "/auth/login", data={"username": "ghost@example.com", "password": "whatever"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos"


# ─── GET /auth/me (get_current_user) ────────────────────────────────────────
def test_me_com_token_valido_retorna_usuario_correto(client):
    token = _register_and_login(client)

    response = client.get("/auth/me", headers=_auth_headers(token))

    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"


def test_me_sem_token_retorna_401(client):
    # Levantado pelo OAuth2PasswordBearer antes de get_current_user rodar —
    # mensagem real é "Not authenticated" (default do FastAPI), por isso não
    # é assertada aqui para não acoplar o teste a texto interno da lib.
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_com_token_malformado_retorna_401(client):
    response = client.get("/auth/me", headers=_auth_headers("not-a-real-token"))

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"


def test_me_com_token_de_usuario_deletado_retorna_401(client, db):
    token = _register_and_login(client)

    user = db.query(User).filter(User.email == "ana@example.com").first()
    db.delete(user)
    db.commit()

    response = client.get("/auth/me", headers=_auth_headers(token))

    assert response.status_code == 401
    assert response.json()["detail"] == "Não foi possível validar as credenciais"
