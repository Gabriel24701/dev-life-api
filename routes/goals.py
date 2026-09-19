from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from models.models import Goal, User
from models.schemas import GoalCreate, GoalUpdate, GoalResponse
from security.auth import get_current_user

router = APIRouter(
    prefix="/goals",
    tags=["Metas"]
)

@router.post("/", response_model=GoalResponse, status_code=201)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria uma nova meta com os dados fornecidos."""
    db_goal = Goal(
        title=goal.title,
        target_date=goal.target_date,
        owner_id=current_user.id
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)

    return db_goal

@router.get("/", response_model=List[GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna a lista de metas apenas do usuário logado."""
    goals = db.query(Goal).filter(Goal.owner_id == current_user.id).all()
    return goals

@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza parcialmente uma meta existente, se pertencer ao usuário logado."""
    db_goal = db.query(Goal).filter(Goal.id == goal_id, Goal.owner_id == current_user.id).first()

    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada ou não pertence a você")

    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)

    db.commit()
    db.refresh(db_goal)

    return db_goal

@router.put("/{goal_id}/complete", response_model=GoalResponse)
def complete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alterna o status de conclusão da meta (toggle), se pertencer ao usuário."""
    db_goal = db.query(Goal).filter(Goal.id == goal_id, Goal.owner_id == current_user.id).first()

    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada ou não pertence a você")

    db_goal.is_completed = not db_goal.is_completed
    db.commit()
    db.refresh(db_goal)

    return db_goal

@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deleta uma meta existente, se pertencer ao usuário."""
    db_goal = db.query(Goal).filter(Goal.id == goal_id, Goal.owner_id == current_user.id).first()

    if not db_goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada ou não pertence a você")

    db.delete(db_goal)
    db.commit()
