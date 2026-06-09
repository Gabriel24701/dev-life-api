from fastapi.testclient import TestClient

# Importa a sua aplicação principal
from main import app 

# Cria um cliente de testes (um "navegador" invisível)
client = TestClient(app)

def test_read_root():
    """
    Testa se a API está de pé respondendo com o código 200 (OK)
    """
    response = client.get("/")
    
    assert response.status_code == 200

@app.get("/")
def healthcheck():
    """
    Rota de Healthcheck para o Kubernetes/Docker saberem que a API está viva.
    """
    return {"status": "ok", "message": "API Dev Life está online!"}