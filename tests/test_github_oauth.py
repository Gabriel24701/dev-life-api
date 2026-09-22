import jwt
import pytest

import routes.github as github_routes
from conftest import _auth_headers, _register_and_login
from security.auth import ALGORITHM, SECRET_KEY


@pytest.fixture(autouse=True)
def _reset_github_module_state(monkeypatch):
    """_used_github_states e _contributions_cache sao caches em memoria de
    modulo (ver routes/github.py) -- sem resetar isso a cada teste, um
    teste vazaria estado pro seguinte (ex.: um jti consumido num teste
    aparecendo como "ja usado" em outro sem relacao nenhuma)."""
    monkeypatch.setattr(github_routes, "_used_github_states", set())
    monkeypatch.setattr(github_routes, "_contributions_cache", {})
    # security/crypto.py tambem cacheia a instancia do Fernet sob demanda;
    # reseta aqui tambem pra encrypt_token/decrypt_token nao dependerem de
    # ordem de execucao com outros arquivos de teste (ex.: test_crypto.py).
    from security import crypto

    monkeypatch.setattr(crypto, "_fernet_instance", None)


class _FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data


def _mock_github_http(
    monkeypatch,
    *,
    access_token="gho_fake123",
    refresh_token=None,
    github_login="octocat",
    token_exchange_status=200,
    contributions_payload=None,
):
    """Mocka as 3 chamadas HTTP reais que routes/github.py faz ao GitHub,
    no ponto de uso (routes.github.requests), mesmo padrao de
    _mock_google_verify (routes.auth_routes.id_token.verify_oauth2_token)
    da Fase 6 -- nunca sai de verdade pra rede em teste."""

    def fake_post(url, **kwargs):
        if url == "https://github.com/login/oauth/access_token":
            body = {"access_token": access_token, "token_type": "bearer"}
            if refresh_token:
                body["refresh_token"] = refresh_token
            return _FakeResponse(body, token_exchange_status)
        if url == "https://api.github.com/graphql":
            return _FakeResponse(contributions_payload or _default_contributions_payload())
        raise AssertionError(f"POST inesperado em teste: {url}")

    def fake_get(url, **kwargs):
        if url == "https://api.github.com/user":
            return _FakeResponse({"login": github_login})
        raise AssertionError(f"GET inesperado em teste: {url}")

    monkeypatch.setattr(github_routes.requests, "post", fake_post)
    monkeypatch.setattr(github_routes.requests, "get", fake_get)


def _default_contributions_payload():
    return {
        "data": {
            "viewer": {
                "contributionsCollection": {
                    "contributionCalendar": {
                        "totalContributions": 3,
                        "weeks": [
                            {
                                "contributionDays": [
                                    {"date": "2026-09-01", "contributionCount": 1},
                                    {"date": "2026-09-02", "contributionCount": 2},
                                ]
                            }
                        ],
                    }
                }
            }
        }
    }


def _make_state(*, user_id, purpose="github_connect", jti="jti-fixo", expires_delta_minutes=10):
    from datetime import datetime, timedelta, timezone

    return jwt.encode(
        {
            "connect_user_id": user_id,
            "purpose": purpose,
            "jti": jti,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_delta_minutes),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ─── /github/authorize ───────────────────────────────────────────────────────
def test_authorize_sem_jwt_retorna_401(client):
    response = client.get("/github/authorize")

    assert response.status_code == 401


def test_authorize_retorna_url_com_state_valido(client, auth_headers):
    response = client.get("/github/authorize", headers=auth_headers)

    assert response.status_code == 200
    url = response.json()["authorize_url"]
    assert url.startswith("https://github.com/login/oauth/authorize?")
    assert "state=" in url
    assert "scope=" not in url  # sem escopo, dado publico nao precisa


# ─── /github/callback: fluxo completo ────────────────────────────────────────
def test_callback_fluxo_completo_salva_token_criptografado_e_username(
    client, auth_headers, monkeypatch, db
):
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY)  # garante Fernet inicializavel
    token = _register_and_login(client, "dono@example.com")
    me = client.get("/auth/me", headers=_auth_headers(token)).json()
    assert me["github_username"] is None

    _mock_github_http(monkeypatch, access_token="gho_plaintext_real", github_login="octocat")
    state = _make_state(user_id=me["id"])

    response = client.get(f"/github/callback?code=abc123&state={state}")

    assert response.status_code == 200
    body = response.json()
    assert body == {"connected": True, "github_username": "octocat"}

    from models.models import User

    user = db.query(User).filter(User.id == me["id"]).first()
    assert user.github_username == "octocat"
    # nunca em texto plano no banco
    assert user.github_access_token != "gho_plaintext_real"
    assert user.github_access_token is not None

    # /auth/me tambem precisa refletir a conexao: e a unica fonte que o
    # frontend tem pra saber, sem chamar /github/*, se ja ha uma conta
    # conectada (ver UserResponse.github_username).
    me_after = client.get("/auth/me", headers=_auth_headers(token)).json()
    assert me_after["github_username"] == "octocat"


def test_callback_com_refresh_token_tambem_criptografa_e_salva(client, monkeypatch, db):
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY)
    token = _register_and_login(client, "comrefresh@example.com")
    me = client.get("/auth/me", headers=_auth_headers(token)).json()

    _mock_github_http(monkeypatch, access_token="gho_x", refresh_token="ghr_plaintext")
    state = _make_state(user_id=me["id"])

    client.get(f"/github/callback?code=abc123&state={state}")

    from models.models import User

    user = db.query(User).filter(User.id == me["id"]).first()
    assert user.github_refresh_token is not None
    assert user.github_refresh_token != "ghr_plaintext"


def test_callback_sem_refresh_token_do_github_mantem_campo_none(client, monkeypatch, db):
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY)
    token = _register_and_login(client, "semrefresh@example.com")
    me = client.get("/auth/me", headers=_auth_headers(token)).json()

    _mock_github_http(monkeypatch, access_token="gho_x")  # sem refresh_token
    state = _make_state(user_id=me["id"])

    client.get(f"/github/callback?code=abc123&state={state}")

    from models.models import User

    user = db.query(User).filter(User.id == me["id"]).first()
    assert user.github_refresh_token is None


# ─── /github/callback: state invalido/expirado/replay ───────────────────────
def test_callback_state_com_assinatura_invalida_retorna_401(client):
    fake_state = jwt.encode(
        {"connect_user_id": 1, "purpose": "github_connect", "jti": "x"},
        "chave-errada-nao-e-a-secret-key-real",
        algorithm=ALGORITHM,
    )

    response = client.get(f"/github/callback?code=abc123&state={fake_state}")

    assert response.status_code == 401
    assert "expirada ou inválida" in response.json()["detail"]


def test_callback_state_expirado_retorna_401(client):
    state = _make_state(user_id=1, expires_delta_minutes=-1)  # ja expirado

    response = client.get(f"/github/callback?code=abc123&state={state}")

    assert response.status_code == 401
    assert "expirada ou inválida" in response.json()["detail"]


def test_callback_state_com_purpose_errado_retorna_401(client):
    state = _make_state(user_id=1, purpose="outro_proposito_qualquer")

    response = client.get(f"/github/callback?code=abc123&state={state}")

    assert response.status_code == 401


def test_callback_state_com_jti_ja_consumido_retorna_401(client, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY)
    token = _register_and_login(client, "replay@example.com")
    me = client.get("/auth/me", headers=_auth_headers(token)).json()

    _mock_github_http(monkeypatch)
    state = _make_state(user_id=me["id"], jti="jti-usado-uma-vez")

    first = client.get(f"/github/callback?code=abc123&state={state}")
    assert first.status_code == 200

    second = client.get(f"/github/callback?code=abc123&state={state}")

    assert second.status_code == 401
    assert "já foi usado" in second.json()["detail"]


def test_callback_code_invalido_retorna_400(client, monkeypatch):
    token = _register_and_login(client, "coderuim@example.com")
    me = client.get("/auth/me", headers=_auth_headers(token)).json()

    def fake_post(url, **kwargs):
        return _FakeResponse({"error": "bad_verification_code"}, 200)

    monkeypatch.setattr(github_routes.requests, "post", fake_post)
    state = _make_state(user_id=me["id"])

    response = client.get(f"/github/callback?code=codigo-invalido&state={state}")

    assert response.status_code == 400


# ─── /github/contributions ───────────────────────────────────────────────────
def test_contributions_sem_github_conectado_retorna_409(client, auth_headers):
    response = client.get("/github/contributions", headers=auth_headers)

    assert response.status_code == 409


def test_contributions_com_github_conectado_retorna_calendario(client, monkeypatch, db):
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY)
    token = _register_and_login(client, "comgithub@example.com")
    me = client.get("/auth/me", headers=_auth_headers(token)).json()

    _mock_github_http(monkeypatch)
    state = _make_state(user_id=me["id"])
    client.get(f"/github/callback?code=abc123&state={state}")

    response = client.get("/github/contributions", headers=_auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["total_contributions"] == 3
    assert body["days"] == [
        {"date": "2026-09-01", "count": 1},
        {"date": "2026-09-02", "count": 2},
    ]


def test_contributions_token_expirado_no_github_retorna_401(client, monkeypatch, db):
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY)
    token = _register_and_login(client, "tokenexpirado@example.com")
    me = client.get("/auth/me", headers=_auth_headers(token)).json()

    _mock_github_http(monkeypatch)
    state = _make_state(user_id=me["id"])
    client.get(f"/github/callback?code=abc123&state={state}")

    def fake_post_401(url, **kwargs):
        return _FakeResponse({"message": "Bad credentials"}, 401)

    monkeypatch.setattr(github_routes.requests, "post", fake_post_401)

    response = client.get("/github/contributions", headers=_auth_headers(token))

    assert response.status_code == 401
    assert "Reconecte sua conta" in response.json()["detail"]


def test_contributions_so_retorna_dado_do_proprio_usuario_logado(client, monkeypatch, db):
    """Ownership: B nunca ve o calendario de A, mesmo que A tenha
    conectado o GitHub -- B simplesmente nao tem github_access_token
    proprio, entao cai no 409 de 'nao conectado', nunca no dado de A."""
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY)
    token_a = _register_and_login(client, "a_github@example.com")
    me_a = client.get("/auth/me", headers=_auth_headers(token_a)).json()

    _mock_github_http(monkeypatch, github_login="dono-a")
    state_a = _make_state(user_id=me_a["id"])
    client.get(f"/github/callback?code=abc123&state={state_a}")

    token_b = _register_and_login(client, "b_github@example.com")

    response = client.get("/github/contributions", headers=_auth_headers(token_b))

    assert response.status_code == 409


# ─── DELETE /github ──────────────────────────────────────────────────────────
def test_disconnect_remove_os_3_campos_localmente(client, monkeypatch, db):
    monkeypatch.setenv("SECRET_KEY", SECRET_KEY)
    token = _register_and_login(client, "desconectar@example.com")
    me = client.get("/auth/me", headers=_auth_headers(token)).json()

    _mock_github_http(monkeypatch)
    state = _make_state(user_id=me["id"])
    client.get(f"/github/callback?code=abc123&state={state}")

    response = client.delete("/github", headers=_auth_headers(token))

    assert response.status_code == 204

    from models.models import User

    user = db.query(User).filter(User.id == me["id"]).first()
    assert user.github_access_token is None
    assert user.github_refresh_token is None
    assert user.github_username is None

    me_after = client.get("/auth/me", headers=_auth_headers(token)).json()
    assert me_after["github_username"] is None
