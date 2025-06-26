from fastapi import FastAPI
from routes import tasks
from models.task import Task
from models.course import Course

app = FastAPI()
app.include_router(tasks.router)




tarefa = Task(
    title="Estudar Python",
    category="Estudos",
    description="Estudar a biblioteca Flask para desenvolvimento de APIs",
    created_at="2023-10-01"
)
print("Iniciando a aplicação...\n")
print(tarefa)
print(tarefa.to_dict())

print()

course = Course(
    title="Curso de Python",
    platform="Alura",
    progress=40,
    start_date="2025-06-25"
)
print(course)
course.update_course(100)
print(course)
print(course.to_dict())

def main():
    
    
    # tarefa.concluir_tarefa()
    pass

if __name__ == "__main__":
    main()
