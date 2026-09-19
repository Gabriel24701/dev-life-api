from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class User(Base):
    __tablename__ = "users"
    # Nome explicito pra bater com a constraint real de producao, criada pela
    # migration manual 0001 (ALTER TABLE ... ADD COLUMN google_sub VARCHAR
    # UNIQUE) antes do Alembic existir. Postgres cria isso como uma UNIQUE
    # CONSTRAINT (nao uma unique INDEX), entao declaramos igual aqui: usar
    # unique=True/index=True no Column geraria um objeto diferente do que
    # ja existe no banco.
    __table_args__ = (
        UniqueConstraint("google_sub", name="users_google_sub_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    auth_provider = Column(String(10), nullable=False, server_default="local")
    google_sub = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tasks = relationship("Task", back_populates="owner")
    habits = relationship("Habit", back_populates="owner")
    study_notes = relationship("StudyNote", back_populates="owner")
    goals = relationship("Goal", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True)
    is_completed = Column(Boolean, default=False)
    priority = Column(String(10), nullable=False, server_default="medium")
    tags = Column(String, nullable=True)
    # Sem timezone=True: divida tecnica, bate com o TIMESTAMP (sem timezone)
    # ja existente em producao. Suporte a timezone e trabalho futuro, caso o
    # app precise (ex.: usuarios em fusos diferentes).
    created_at = Column(DateTime, server_default=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tasks")


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    streak = Column(Integer, default=0)
    last_completed_at = Column(Date, nullable=True)
    # Sem timezone=True: divida tecnica, bate com o TIMESTAMP (sem timezone)
    # ja existente em producao. Suporte a timezone e trabalho futuro, caso o
    # app precise (ex.: usuarios em fusos diferentes).
    created_at = Column(DateTime, server_default=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="habits")

class StudyNote(Base):
    __tablename__ = "study_notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    tags = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="study_notes")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    target_date = Column(DateTime(timezone=True))
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="goals")