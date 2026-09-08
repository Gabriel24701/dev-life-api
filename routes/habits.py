from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta, timezone, datetime
from database.database import get_db
from models.models import Habit, User
from models.schemas import HabitCreate, HabitUpdate, HabitResponse
from security.auth import get_current_user

router = APIRouter(
    prefix="/habits",
    tags=["Hábitos"]
)

class AlreadyCompletedTodayError(Exception):
    """Levantada quando o hábito já foi marcado como concluído no dia civil de hoje."""
    pass

def compute_new_streak(current_streak: int, last_completed_at: date | None, today: date) -> int:
    """Calcula o novo streak a partir do último dia de conclusão e do dia de hoje (dia civil)."""
    if last_completed_at == today:
        raise AlreadyCompletedTodayError()
    if last_completed_at == today - timedelta(days=1):
        return current_streak + 1
    # None (nunca concluído) ou mais antigo que ontem (pulou um dia) -> reinicia a sequência
    return 1

@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit: HabitCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria um novo hábito atrelado ao usuário logado."""
    new_habit = Habit(title=habit.title, description=habit.description, owner_id=current_user.id)
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

@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza parcialmente um hábito existente, se pertencer ao usuário logado."""
    db_habit = db.query(Habit).filter(Habit.id == habit_id, Habit.owner_id == current_user.id).first()

    if not db_habit:
        raise HTTPException(status_code=404, detail="Hábito não encontrado ou não pertence a você")

    update_data = habit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_habit, field, value)

    db.commit()
    db.refresh(db_habit)

    return db_habit

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

    # Dia civil calculado em UTC — simplificação conhecida: não considera o fuso horário
    # do usuário (não existe campo de timezone no User hoje). Streak por fuso do usuário
    # fica como trabalho futuro.
    today = datetime.now(timezone.utc).date()
    try:
        db_habit.streak = compute_new_streak(db_habit.streak, db_habit.last_completed_at, today)
    except AlreadyCompletedTodayError:
        raise HTTPException(status_code=409, detail="Hábito já concluído hoje.")

    db_habit.last_completed_at = today
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