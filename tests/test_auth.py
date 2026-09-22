import importlib

import pytest

import security.auth as auth_module
from conftest import _auth_headers, _register_and_login
from models.models import User

# Valor que tests/conftest.py seta antes da collection (from main import app
# importa security/auth.py, que exige SECRET_KEY no import do modulo).
# Reaproveitado aqui pra devolver o modulo ao mesmo estado que o resto da
# suite espera, apos o reload forcado do teste abaixo.
_TEST_SECRET_KEY = "test-secret-key-not-for-production"


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


def test_register_sucesso_publica_evento_user_created(client, monkeypatch):
    published = {}
    monkeypatch.setattr(
        "routes.auth_routes.publish_user_created", lambda **kwargs: published.update(kwargs)
    )

    response = client.post(
        "/auth/register",
        json={"name": "Bia", "email": "bia@example.com", "password": "secret123"},
    )

    assert response.status_code == 201
    assert published["email"] == "bia@example.com"
    assert published["auth_provider"] == "local"
    assert isinstance(published["user_id"], int)


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
    # Confirmado manualmente: mesmo status e mesma mensagem que senha errada.
    # O endpoint não vaza quais e-mails estão cadastrados.
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
    # github_username so aparece depois de conectar via /github/callback
    assert response.json()["github_username"] is None


def test_me_sem_token_retorna_401(client):
    # Levantado pelo OAuth2PasswordBearer antes de get_current_user rodar;
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


# ─── PUT /auth/me ────────────────────────────────────────────────────────────
def test_update_me_sucesso_atualiza_nome(client):
    token = _register_and_login(client)

    response = client.put(
        "/auth/me", json={"name": "Novo Nome"}, headers=_auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Novo Nome"

    # confirma persistência: uma nova leitura reflete o valor salvo
    me = client.get("/auth/me", headers=_auth_headers(token))
    assert me.json()["name"] == "Novo Nome"


def test_update_me_nome_vazio_retorna_422(client):
    token = _register_and_login(client)

    response = client.put("/auth/me", json={"name": ""}, headers=_auth_headers(token))

    assert response.status_code == 422


# ─── SECRET_KEY ausente no import do modulo ─────────────────────────────────
def test_secret_key_ausente_no_import_levanta_runtime_error(monkeypatch):
    """security/auth.py le SECRET_KEY no import do modulo, sem fallback:
    sem a variavel no ambiente, o import deve falhar alto e claro em vez de
    cair silenciosamente numa chave conhecida (o problema original que
    motivou remover o fallback hardcoded). Usa importlib.reload pra forcar
    o corpo do modulo a reexecutar sem SECRET_KEY.

    O finally reimporta com SECRET_KEY restaurada, sempre -- o resto da
    suite depende do modulo carregado com sucesso (tests/conftest.py seta
    SECRET_KEY antes da collection, e funcoes como get_current_user usam a
    SECRET_KEY do modulo ao vivo, nao uma copia)."""
    monkeypatch.delenv("SECRET_KEY", raising=False)

    try:
        with pytest.raises(
            RuntimeError, match="SECRET_KEY precisa estar definida para assinar tokens JWT."
        ):
            importlib.reload(auth_module)
    finally:
        monkeypatch.setenv("SECRET_KEY", _TEST_SECRET_KEY)
        importlib.reload(auth_module)
