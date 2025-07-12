from fastapi import APIRouter
from models.task import TaskCreate
import sqlite3

router = APIRouter()

tasks = []

@router.get("/tasks")
def get_tasks():
    conn = sqlite3.connect("C:/projetos/dev-life-api/database/devlife.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    tasks = []
    for row in rows:
        task = {
            "id": row[0],
            "title": row[1],
            "category": row[2],
            "description": row[3],
            "status": row[4],
            "created_at": row[5]
        }
        tasks.append(task)

    conn.close()
    return tasks


@router.post("/tasks")
def create_task(task: TaskCreate):
    conn = sqlite3.connect("devlife.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, category, description, created_at)
        VALUES (?, ?, ?, ?)
    """, (task.title, task.category, task.description, task.created_at))

    conn.commit()
    conn.close()
    return {"message": "Tarefa salva com sucesso!"}

@router.patch("/tasks/{task_id}")
def update_task_status(task_id: int):
    if 0 <= task_id < len(tasks):
        tasks[task_id].concluir_tarefa()
        return {"message": "Tarefa marcada como completa."}
    return {"error": "Tarefa não encontrada."}
