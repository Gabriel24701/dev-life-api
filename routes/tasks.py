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
    conn = sqlite3.connect("database/devlife.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, category, description, created_at)
        VALUES (?, ?, ?, ?)
    """, (task.title, task.category, task.description, task.created_at))

    conn.commit()
    conn.close()
    return {"message": "Tarefa salva com sucesso!"}

@router.patch("/tasks/{task_id}")
def conclude_task(task_id: int):
    conn = sqlite3.connect("database/devlife.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        return {"error": "Tarefa não encontrada."}

    cursor.execute("""
        UPDATE tasks
        SET status = 1
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    return {"message": "Tarefa marcada como concluída com sucesso!"}

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = sqlite3.connect("database/devlife.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        return {"error": "Tarefa não encontrada."}
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Tarefa deletada com sucesso!"}