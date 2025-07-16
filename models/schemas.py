from pydantic import BaseModel, Field
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, example="Estudar FastAPI")
    category: str = Field(..., example="Estudo")
    description: str = Field(..., example="Ler a documentação oficial do FastAPI")
    created_at: datetime = Field(..., example="2024-07-15T14:00:00")

class HabitCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=150, example="Beber água")
    category: str = Field(..., example="Saúde")
    goal_type: str = Field(..., example="Diário")
    target: int = Field(..., ge=1, description="Meta mínima para o hábito", example=3)
    created_at: datetime = Field(..., example="2024-07-15T14:00:00")

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, example="Python para Iniciantes")
    platform: str = Field(..., min_length=3, max_length=100, example="Udemy")
    progress: int = Field(..., ge=0, le=100, description="Progresso do curso de 0 a 100", example=50)
    start_date: datetime = Field(..., example="2024-07-15T14:00:00")

class CourseUpdate(BaseModel):
    progress: int = Field(..., ge=0, le=100, description="Progresso do curso de 0 a 100", example=80)