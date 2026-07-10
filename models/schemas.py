from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True
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

class HabitBase(BaseModel):
    title: str
    description: Optional[str] = None

class HabitCreate(BaseModel):
    title: str

class HabitResponse(BaseModel):
    id: int
    title: str
    streak: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class StudyNoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None

class StudyNoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: Optional[str] = None
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class GoalCreate(BaseModel):
    title: str
    target_date: datetime

class GoalResponse(BaseModel):
    id: int
    title: str
    target_date: datetime
    is_completed: bool
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True