from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dev Life API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes import tasks, habits
app.include_router(tasks.router)
app.include_router(habits.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à Dev Life API!", "status": "Online e Conectada ao Banco de Dados"}