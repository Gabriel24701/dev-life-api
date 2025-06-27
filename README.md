
# 🚀 Dev Life API

Uma API de produtividade pessoal desenvolvida em Python com FastAPI, com foco em rastreamento de tarefas, cursos e hábitos.

---

## 📌 Funcionalidades

- ✅ Criar, listar e concluir tarefas (`Task`)
- 📚 Acompanhar progresso de cursos (`Course`)
- 🔁 Rastrear hábitos diários com streak (`Habit`)

---

## 🛠 Tecnologias utilizadas

- Python 3.11+
- FastAPI
- Uvicorn

---

## 📂 Estrutura do projeto

```
dev-life-api/
│
├── models/
│   ├── task.py
│   ├── course.py
│   └── habit.py
├── routes/
│   ├── tasks.py
│   ├── courses.py
│   └── habits.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

---

## ▶️ Como rodar localmente

1. Clone o repositório:

```bash
git clone https://github.com/Gabriel24701/dev-life-api.git
cd dev-life-api
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate  # No Windows
```

3. Instale as dependências:

```bash
pip install fastapi uvicorn
```

4. Rode o servidor local:

```bash
uvicorn main:app --reload
```

5. Acesse a documentação interativa:

- [http://localhost:8000/docs]

---

## 🧪 Endpoints principais

### 📝 Tarefas
- `GET /tasks`
- `POST /tasks`
- `PATCH /tasks/{task_id}`

### 📘 Cursos
- `GET /courses`
- `POST /courses`
- `PATCH /courses/{course_id}`

### 🔁 Hábitos
- `GET /habits`
- `POST /habits`
- `PATCH /habits/{habit_id}`

---

## 📈 Próximos passos

- [ ] Implementar persistência com SQLite
- [ ] Criar painel visual com frontend (futuro)

---

## 👨‍💻 Autor

**Gabriel Bebé Silva**  
Estudante de Análise e Desenvolvimento de Sistemas — FIAP  
[LinkedIn](www.linkedin.com/in/gabriel-bebé-298815238)
