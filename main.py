from fastapi import FastAPI
from routes import tasks, courses, habits
from models.task import Task
from models.course import Course
from models.habit import Habit

app = FastAPI()
app.include_router(tasks.router)
app.include_router(courses.router)
app.include_router(habits.router)

def test_models():
    print("Iniciando a aplicação...\n")

    # Testando Task
    tarefa = Task(
        title="Estudar Python",
        category="Estudos",
        description="Estudar a biblioteca Flask para desenvolvimento de APIs",
        created_at="2023-10-01"
    )
    print(f"{tarefa}\n{tarefa.to_dict()}\n")

    # Testando Course
    course = Course(
        title="Curso de Python",
        platform="Alura",
        progress=40,
        start_date="2025-06-25"
    )
    print(course)
    course.update_progress(100)
    print(course)
    print(course.to_dict(), "\n")

    # Testando Habit
    habit = Habit("Beber agua", "saude", "diariamente", 5, "2025/06/26")
    print(habit)
    print(habit.to_dict())
    habit.mark_today()
    print(habit.to_dict())

if __name__ == "__main__":
    test_models()