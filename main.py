from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models.models import Base

# 1. MÁGICA DO BANCO: Cria as tabelas se elas não existirem
Base.metadata.create_all(bind=engine) # <-- CORREÇÃO AQUI: Usamos apenas Base.metadata

# 2. INICIALIZAÇÃO: Cria o app uma única vez
app = FastAPI(title="Dev Life API", version="2.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#ROTAS
from routes import tasks, habits
app.include_router(tasks.router)
app.include_router(habits.router)

#Healthcheck)
@app.get("/")
def read_root():
    return {"message": "Bem-vindo à Dev Life API!", "status": "Online e Conectada ao Banco de Dados"}