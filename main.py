from fastapi import FastAPI
from routes import tasks
from models.task import Task

app = FastAPI()
app.include_router(tasks.router)




tarefa = Task(
    title="Estudar Python",
    category="Estudos",
    description="Estudar a biblioteca Flask para desenvolvimento de APIs",
    created_at="2023-10-01"
)
print("Iniciando a aplicação...")
print(tarefa)
print(tarefa.to_dict())

def main():
    
    # tarefa.concluir_tarefa()
    pass

if __name__ == "__main__":
    main()
