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

@router.patch("/tasks/{task_id}")
def update_task_status(task_id: int):
    if 0 <= task_id < len(tasks):
        tasks[task_id].concluir_tarefa()
        return {"message": "Tarefa marcada como completa."}
    return {"error": "Tarefa não encontrada."}
