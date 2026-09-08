# 🚀 Dev Life API

Uma API de produtividade pessoal desenvolvida em Python com FastAPI, com foco em rastreamento de tarefas, cursos e hábitos.

> 💡 **Por que escolhi esse projeto?**  
> Ao entrar de vez no mundo da tecnologia, percebi que organização é essencial para manter a constância nos estudos e no desenvolvimento pessoal.  
> Eu mesmo precisava de uma forma prática de acompanhar minhas tarefas, cursos e hábitos diários então resolvi criar essa API para resolver um **problema real da minha rotina**.  
> Uma vida organizada é, sem dúvidas, muito mais produtiva. E foi assim que surgiu a ideia do **Dev Life API**.

---

## 📌 Funcionalidades

- ✅ Criar, listar, concluir e deletar tarefas (`Task`)
- 📚 Acompanhar progresso de cursos (`Course`)
- 🔁 Rastrear hábitos diários com streak (`Habit`)

---

## 🛠 Tecnologias utilizadas

-


- Python 3.11+
- FastAPI
- Uvicorn
- SQLite3

---

## 📂 Estrutura do projeto

```
dev-life-api/
│
├── database/
│   ├── database.py         # Função utilitária para conexão SQLite
│   └── init_db.py          # Script para criação das tabelas
├── models/
│   ├── task.py
│   ├── course.py
│   ├── habit.py
│   └── schemas.py          # Modelos Pydantic (validação/serialização)
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

1. **Clone o repositório:**

```bash
git clone https://github.com/Gabriel24701/dev-life-api.git
cd dev-life-api
```

2. **Crie e ative um ambiente virtual:**

```bash
python -m venv venv
venv\Scripts\activate  # No Windows
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Inicialize o banco de dados (criação das tabelas):**

```bash
python database/init_db.py
```

5. **Rode o servidor local:**

```bash
uvicorn main:app --reload
```

6. **Acesse a documentação interativa:**

- [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔑 Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `SECRET_KEY` | Recomendada | Assina os tokens JWT. Tem um valor padrão de desenvolvimento no código, mas deve ser sobrescrita em produção. |
| `DATABASE_URL` | Não | String de conexão do banco (Postgres em produção). Sem ela, cai no SQLite local (`devlife_local.db`). |
| `GOOGLE_CLIENT_ID` | **Sim, para login via Google** | Client ID OAuth do Google, usado por `POST /auth/google` para validar a audiência (`aud`) do ID token recebido do frontend. **Sem essa variável configurada, `/auth/google` falha ao verificar qualquer token** — a rota fica inutilizável, mesmo com um token do Google legítimo. |

**Onde configurar:**
- **Produção (Azure):** App Service → *Configuration* → *Application Settings*.
- **Desenvolvimento local:** o projeto **não carrega `.env` automaticamente** (não usa `python-dotenv`) — exporte a variável no shell antes de rodar o servidor, por exemplo:
  ```bash
  # Windows (cmd)
  set GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
  uvicorn main:app --reload
  ```
  ```bash
  # PowerShell
  $env:GOOGLE_CLIENT_ID = "seu-client-id.apps.googleusercontent.com"
  uvicorn main:app --reload
  ```

---

## 🧪 Endpoints principais

### 📝 Tarefas
- `GET /tasks`
- `POST /tasks`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

### 📘 Cursos
- `GET /courses`
- `POST /courses`
- `PATCH /courses/{course_id}`
- `DELETE /courses/{course_id}`

### 🔁 Hábitos
- `GET /habits`
- `POST /habits`
- `PATCH /habits/{habit_id}`
- `DELETE /habits/{habit_id}`

---

## 👨‍💻 Autor

**Gabriel Bebé Silva**  
Estudante de Análise e Desenvolvimento de Sistemas — FIAP  
[LinkedIn](https://www.linkedin.com/in/gabriel-bebé-298815238)