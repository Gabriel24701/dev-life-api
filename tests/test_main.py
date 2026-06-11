from fastapi.testclient import TestClient
from main import app

# O TestClient simula um navegador acessando a nossa API sem precisar ligar o servidor de verdade
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à Dev Life API!", "status": "Online e Conectada ao Banco de Dados"}