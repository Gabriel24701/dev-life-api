from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from models.models import Task, User
from models.schemas import TaskCreate, TaskUpdate, TaskResponse
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
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        tags=task.tags,
        owner_id=current_user.id
    )
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

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza parcialmente uma tarefa existente, se pertencer ao usuário logado."""
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada ou não pertence a você")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)

    return db_task

@router.put("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alterna o status de conclusão da tarefa (toggle), se pertencer ao usuário."""
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada ou não pertence a você")

    db_task.is_completed = not db_task.is_completed
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