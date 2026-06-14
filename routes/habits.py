from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.models import Habit
from models.schemas import HabitCreate, HabitResponse

router = APIRouter(
    prefix="/habits",
    tags=["Hábitos"]
)

# ==========================================
# 1. CRIAR UM HÁBITO (POST)
# ==========================================
@router.post("/", response_model=HabitResponse, status_code=201)
def create_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    db_habit = Habit(title=habit.title, description=habit.description)
    
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    
    return db_habit

# ==========================================
# 2. LISTAR TODOS OS HÁBITOS (GET)
# ==========================================
@router.get("/", response_model=List[HabitResponse])
def get_habits(db: Session = Depends(get_db)):
    return db.query(Habit).all()

# ==========================================
# 3. MARCAR HÁBITO DO DIA / AUMENTAR OFENSIVA (PUT)
# ==========================================
@router.put("/{habit_id}/mark", response_model=HabitResponse)
def mark_habit_today(habit_id: int, db: Session = Depends(get_db)):
    db_habit = db.query(Habit).filter(Habit.id == habit_id).first()
    
    if not db_habit:
        raise HTTPException(status_code=404, detail="Hábito não encontrado")
    
    db_habit.streak += 1
    
    db.commit()
    db.refresh(db_habit)
    
    return db_habit

# ==========================================
# 4. DELETAR UM HÁBITO (DELETE)
# ==========================================
@router.delete("/{habit_id}", status_code=204)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    db_habit = db.query(Habit).filter(Habit.id == habit_id).first()
    
    if not db_habit:
        raise HTTPException(status_code=404, detail="Hábito não encontrado")
    
    db.delete(db_habit)
    db.commit()
    return