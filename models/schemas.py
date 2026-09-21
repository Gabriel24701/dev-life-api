from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal

PriorityLevel = Literal["low", "medium", "high"]

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str = Field(min_length=1)

class GoogleLoginPayload(BaseModel):
    credential: str

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
    priority: Optional[PriorityLevel] = "medium"
    tags: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    tags: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    priority: PriorityLevel
    tags: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HabitBase(BaseModel):
    title: str
    description: Optional[str] = None

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class HabitResponse(HabitBase):
    id: int
    streak: int
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class StudyNoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None

class StudyNoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
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

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    target_date: Optional[datetime] = None

class GoalResponse(BaseModel):
    id: int
    title: str
    target_date: datetime
    is_completed: bool
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class GitHubAuthorizeResponse(BaseModel):
    authorize_url: str

# Nunca inclui o token, so a confirmacao de que a conexao funcionou e o
# username publico associado a ela.
class GitHubConnectionResponse(BaseModel):
    connected: bool
    github_username: Optional[str] = None

class GitHubContributionDay(BaseModel):
    date: str
    count: int

class GitHubContributionsResponse(BaseModel):
    total_contributions: int
    days: List[GitHubContributionDay]