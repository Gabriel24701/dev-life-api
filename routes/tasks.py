from fastapi import APIRouter, HTTPException
from models.schemas import TaskCreate
from typing import List
from database.database import get_db

router = APIRouter()

@router.get("/tasks", response_model=List[TaskCreate])
def get_tasks():
    """
    Retorna a lista de todas as tarefas cadastradas.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, category, description, created_at FROM tasks")
            rows = cursor.fetchall()
            return [
                TaskCreate(
                    title=row[0],
                    category=row[1],
                    description=row[2],
                    created_at=row[3]
                ) for row in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks")
def create_task(task: TaskCreate):
    """Cria uma nova tarefa com os dados fornecidos.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (title, category, description, created_at)
                VALUES (?, ?, ?, ?)
            """, (task.title, task.category, task.description, task.created_at))
            conn.commit()
            return {"id": cursor.lastrowid, "message": "Tarefa salva com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/tasks/{task_id}")
def conclude_task(task_id: int):
    """Marca uma tarefa como concluída.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            task = cursor.fetchone()

            if task is None:
                if task is None:
                    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
            cursor.execute("""
                UPDATE tasks
                SET status = 1
                WHERE id = ?
            """, (task_id,))

            conn.commit()
            return {"message": "Tarefa marcada como concluída com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """Deleta uma tarefa com base no ID fornecido.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            task = cursor.fetchone()

            if task is None:
                conn.close()
                if task is None:
                    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
            
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return {"message": "Tarefa deletada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))