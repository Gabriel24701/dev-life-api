from fastapi import APIRouter
from models.task import Task

router = APIRouter()

tasks = []

@router.get("/tasks")
def get_tasks():
    return [task.to_dict() for task in tasks]

@router.post("/tasks")
def create_task(title: str, category: str, description: str, date: str):
    new_task = Task(title, category, description, date)
    tasks.append(new_task)
    return {"mensagem": "Tarefa criada com sucesso!"}
