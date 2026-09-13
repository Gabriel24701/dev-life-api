from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine
from models.models import Base
from routes import auth_routes

# create_all so roda no fallback SQLite local (conveniencia de dev/onboarding).
# Em producao (Postgres) o schema e gerenciado pelo Alembic (ver alembic/),
# entao nao queremos dois mecanismos alterando o schema de producao.
if engine.name == "sqlite":
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dev Life API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://dev-life-web.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes import tasks, habits
app.include_router(tasks.router)
app.include_router(habits.router)
app.include_router(auth_routes.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à Dev Life API!", "status": "Online e Conectada ao Banco de Dados"}