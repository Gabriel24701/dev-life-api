from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from models.models import Task, User
from models.schemas import TaskCreate, TaskResponse
from security.auth import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["Tarefas"]
)

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria uma nova tarefa com os dados fornecidos."""
    db_task = Task(title=task.title, description=task.description, owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna a lista de tarefas apenas do usuário logado."""
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return tasks

@router.put("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marca uma tarefa como concluída, se pertencer ao usuário."""
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada ou não pertence a você")
    
    db_task.is_completed = True
    db.commit()
    db.refresh(db_task)
    
    return db_task

@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta uma tarefa existente, se pertencer ao usuário."""
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada ou não pertence a você")
    
    db.delete(db_task)
    db.commit()