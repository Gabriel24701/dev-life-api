import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    """Sessão de banco isolada por teste: schema criado antes, derrubado depois."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """TestClient com get_db substituído pela sessão in-memory do teste."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _register_and_login(client, email="ana@example.com", password="secret123"):
    """Registra e loga um usuário via API, retornando o access_token."""
    client.post("/auth/register", json={"name": email, "email": email, "password": password})
    response = client.post("/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers(client):
    """Headers de autenticação prontos para um único usuário de teste padrão."""
    token = _register_and_login(client)
    return _auth_headers(token)
