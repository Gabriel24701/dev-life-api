from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Importando a nossa conexão com o banco e os nossos moldes
from database import get_db
from models.models import Task
from models.schemas import TaskCreate, TaskResponse

# Cria o "Roteador" (como se fosse um mini-FastAPI focado só em tarefas)
router = APIRouter(
    prefix="/tasks",
    tags=["Tarefas"]
)

# ==========================================
# 1. CRIAR UMA TAREFA (POST)
# ==========================================
@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Transforma o schema (Pydantic) no modelo do banco (SQLAlchemy)
    db_task = Task(title=task.title, description=task.description)
    
    # Adiciona, salva e atualiza a variável com o ID gerado pelo banco
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

# ==========================================
# 2. LISTAR TODAS AS TAREFAS (GET)
# ==========================================
@router.get("/", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    # Equivalente ao SQL: SELECT * FROM tasks;
    tasks = db.query(Task).all()
    return tasks

# ==========================================
# 3. CONCLUIR UMA TAREFA (PUT)
# ==========================================
@router.put("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    # Busca a tarefa no banco pelo ID
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    # Atualiza o status e salva
    db_task.is_completed = True
    db.commit()
    db.refresh(db_task)
    
    return db_task

# ==========================================
# 4. DELETAR UMA TAREFA (DELETE)
# ==========================================
@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    db.delete(db_task)
    db.commit()
    return # Retorna vazio com status 204 (No Content)