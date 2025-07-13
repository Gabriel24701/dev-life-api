from fastapi import APIRouter
from models.habit import Habit, HabitCreate
import sqlite3
import json

router = APIRouter()

@router.get("/habits")
def get_habits():
    conn = sqlite3.connect("database/devlife.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits")
    rows = cursor.fetchall()
    habits = []
    
    for row in rows:
        completed_dates = json.loads(row[6]) if row[6] else []  # ← aqui o pulo do gato
        habit = {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "goal_type": row[3],
            "target": row[4],
            "created_at": row[5],
            "completed_dates": completed_dates
        }
        habits.append(habit)

    conn.close()
    return habits


@router.post("/habits")
def create_habit(habit: HabitCreate):
    conn = sqlite3.connect("database/devlife.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO habits (name, category, goal_type, target, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (habit.name, habit.category, habit.goal_type, habit.target, habit.created_at))
    conn.commit()
    conn.close()
    return {"message": "Hábito criado com sucesso!"}


@router.patch("/habits/{habit_id}")
def update_habit_status(habit_id: int):
    if 0 <= habit_id < len(habits):
        habits[habit_id].mark_today()
        return {"message": "Hábito marcado como concluído."}
    return {"error": "Hábito não encontrado."}