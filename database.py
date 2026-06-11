import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# A Azure vai injetar a DATABASE_URL automaticamente nas variáveis de ambiente.
# Se a variável não existir (como no seu PC local), ele cria um arquivo SQLite chamado 'devlife_local.db' para você não travar o desenvolvimento!
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./devlife_local.db")

# O SQLAlchemy exige que o prefixo seja 'postgresql://' e não apenas 'postgres://'
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuração do Motor do Banco de Dados
# O 'check_same_thread' é necessário apenas para o SQLite local não dar erro
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# Cria a fábrica de sessões (as "conversas" com o banco)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base que vamos usar para criar as nossas tabelas depois
Base = declarative_base()

# Função auxiliar para injetar o banco de dados nas nossas rotas do FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()