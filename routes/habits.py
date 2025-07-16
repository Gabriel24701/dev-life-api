from fastapi import APIRouter, HTTPException, status
from models.schemas import HabitCreate
from typing import List
import json
import datetime
from database.database import get_db

router = APIRouter()

@router.get("/habits", response_model=List[HabitCreate])
def get_habits():
    """Retorna a lista de todos os hábitos cadastrados."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habits")
            rows = cursor.fetchall()
            habits = []
            for row in rows:
                completed_dates = json.loads(row[6]) if row[6] else []
                return [
                    HabitCreate(
                        id=row[0],
                        name=row[1],
                        category=row[2],
                        goal_type=row[3],
                        target=row[4],
                        created_at=row[5],
                        completed_dates=completed_dates
                    )
                ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/habits")
def create_habit(habit: HabitCreate):
    """Cria um novo hábito com os dados fornecidos."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO habits (name, category, goal_type, target, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (habit.name, habit.category, habit.goal_type, habit.target, habit.created_at))
            conn.commit()
            return {"id": cursor.lastrowid, "message": "Hábito salvo com sucesso!"}, status.HTTP_201_CREATED
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import datetime

@router.patch("/habits/{habit_id}")
def update_habit_status(habit_id: int):
    """Marca o hábito como concluído para o dia atual."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT completed_dates FROM habits WHERE id = ?", (habit_id,))
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Hábito não encontrado.")
            completed_dates = json.loads(row[0]) if row[0] else []
            today = datetime.date.today().isoformat()
            if today not in completed_dates:
                completed_dates.append(today)
            cursor.execute(
                "UPDATE habits SET completed_dates = ? WHERE id = ?",
                (json.dumps(completed_dates), habit_id)
            )
            conn.commit()
            return {"message": "Hábito marcado como concluído."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    