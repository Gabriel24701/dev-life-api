from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from models.models import Habit, User
from models.schemas import HabitCreate, HabitResponse
from security.auth import get_current_user

router = APIRouter(
    prefix="/habits",
    tags=["Hábitos"]
)

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit: HabitCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria um novo hábito atrelado ao usuário logado."""
    new_habit = Habit(title=habit.title, owner_id=current_user.id)
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@router.get("/", response_model=List[HabitResponse])
def get_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna os hábitos apenas do usuário logado."""
    habits = db.query(Habit).filter(Habit.owner_id == current_user.id).all()
    return habits

@router.put("/{habit_id}/increment", response_model=HabitResponse)
def increment_streak(
    habit_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aumenta a contagem de dias seguidos (streak) do hábito."""
    db_habit = db.query(Habit).filter(Habit.id == habit_id, Habit.owner_id == current_user.id).first()
    
    if not db_habit:
        raise HTTPException(status_code=404, detail="Hábito não encontrado ou não pertence a você")
    
    db_habit.streak += 1
    db.commit()
    db.refresh(db_habit)
    return db_habit

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta um hábito existente."""
    db_habit = db.query(Habit).filter(Habit.id == habit_id, Habit.owner_id == current_user.id).first()
    
    if not db_habit:
        raise HTTPException(status_code=404, detail="Hábito não encontrado ou não pertence a você")
    
    db.delete(db_habit)
    db.commit()