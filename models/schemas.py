from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ==========================================
# SCHEMAS PARA TAREFAS (Tasks)
# ==========================================

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass
class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# SCHEMAS PARA HÁBITOS (Habits)
# ==========================================

class HabitBase(BaseModel):
    title: str
    description: Optional[str] = None

class HabitCreate(HabitBase):
    pass

class HabitResponse(HabitBase):
    id: int
    streak: int
    created_at: datetime

    class Config:
        from_attributes = True