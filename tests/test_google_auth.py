from conftest import _auth_headers, _register_and_login
from models.models import User


def _mock_google_verify(monkeypatch, *, email, sub, name="Google User", email_verified=True):
    def fake_verify(*args, **kwargs):
        return {
            "email": email,
            "sub": sub,
            "name": name,
            "email_verified": email_verified,
        }

    monkeypatch.setattr("routes.auth_routes.id_token.verify_oauth2_token", fake_verify)


# ─── POST /auth/google ───────────────────────────────────────────────────────
def test_google_login_cria_conta_nova(client, monkeypatch, db):
    _mock_google_verify(
        monkeypatch, email="nova@example.com", sub="google-sub-123", name="Nova Pessoa"
    )

    response = client.post("/auth/google", json={"credential": "fake-credential"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    user = db.query(User).filter(User.email == "nova@example.com").first()
    assert user is not None
    assert user.auth_provider == "google"
    assert user.hashed_password is None
    assert user.google_sub == "google-sub-123"


def test_google_login_recorrente_nao_duplica_conta(client, monkeypatch, db):
    _mock_google_verify(
        monkeypatch,
        email="recorrente@example.com",
        sub="google-sub-456",
        name="Pessoa Recorrente",
    )

    first = client.post("/auth/google", json={"credential": "fake-credential"})
    second = client.post("/auth/google", json={"credential": "fake-credential"})

    assert first.status_code == 200
    assert second.status_code == 200

    users = db.query(User).filter(User.email == "recorrente@example.com").all()
    assert len(users) == 1

    me1 = client.get("/auth/me", headers=_auth_headers(first.json()["access_token"])).json()
    me2 = client.get("/auth/me", headers=_auth_headers(second.json()["access_token"])).json()
    assert me1["id"] == me2["id"]


def test_google_login_colisao_com_conta_local_retorna_409(client, monkeypatch):
    _register_and_login(client, email="jalocal@example.com")

    _mock_google_verify(monkeypatch, email="jalocal@example.com", sub="google-sub-999")

    response = client.post("/auth/google", json={"credential": "fake-credential"})

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Já existe uma conta com este e-mail. Faça login com sua senha."
    )


# ─── Interação com o login por senha ─────────────────────────────────────────
def test_login_por_senha_continua_funcionando_apos_guard(client):
    """Confirma que o guard contra hashed_password None não quebrou o
    caminho feliz do login por senha comum."""
    client.post(
        "/auth/register",
        json={"name": "Ana", "email": "ana2@example.com", "password": "secret123"},
    )

    response = client.post(
        "/auth/login", data={"username": "ana2@example.com", "password": "secret123"}
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_por_senha_em_conta_google_only_retorna_401(client, monkeypatch):
    _mock_google_verify(
        monkeypatch, email="google-only@example.com", sub="google-sub-only"
    )
    client.post("/auth/google", json={"credential": "fake-credential"})

    response = client.post(
        "/auth/login",
        data={"username": "google-only@example.com", "password": "qualquer-coisa"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos"
