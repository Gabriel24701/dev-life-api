from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ==========================================
# SCHEMAS PARA TAREFAS (Tasks)
# ==========================================

# 1. Base: O que é comum em todas as operações
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

# 2. Create: O que o usuário MANDA para a API quando quer criar uma tarefa
class TaskCreate(TaskBase):
    pass # Herda tudo de TaskBase, não precisa adicionar nada agora

# 3. Response: O que a API DEVOLVE para o usuário (inclui os dados gerados pelo Banco)
class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True # Essencial! Ensina o Pydantic a ler o objeto do SQLAlchemy

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