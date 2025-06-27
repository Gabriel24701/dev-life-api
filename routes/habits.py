from fastapi import APIRouter
from models.habit import Habit

router = APIRouter()
habits = []

@router.get("/habits")
def get_habits():
    return [habit.to_dict() for habit in habits]

@router.post("/habits")
def create_habit(name: str, category: str, goal_type: str, target: int, created_at: str):
    new_habit = Habit(name, category, goal_type, target, created_at)
    habits.append(new_habit)
    return {"message": "Hábito criado com sucesso!"}

@router.patch("/habits/{habit_id}")
def update_habit_status(habit_id: int):
    if 0 <= habit_id < len(habits):
        habits[habit_id].mark_today()
        return {"message": "Hábito marcado como concluído."}
    return {"error": "Hábito não encontrado."}