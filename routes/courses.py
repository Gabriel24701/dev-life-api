from fastapi import APIRouter, HTTPException, status
from models.schemas import CourseCreate, CourseUpdate
from typing import List
from database.database import get_db

router = APIRouter()

@router.get("/courses", response_model=List[CourseCreate])
def get_courses():
    """Retorna a lista de todos os cursos cadastrados.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, platform, progress, start_date FROM courses")
            rows = cursor.fetchall()
            return [
                CourseCreate(
                    title=row[0],
                    platform=row[1],
                    progress=row[2],
                    start_date=row[3]
                ) for row in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/courses")
def create_course(course: CourseCreate):
    """Cria um novo curso com os dados fornecidos.
    """
    completed = 1 if course.progress >= 100 else 0
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO courses (title, platform, progress, start_date, completed)
                VALUES (?, ?, ?, ?, ?)
            """, (course.title, course.platform, course.progress, course.start_date, completed))
            return {"id": cursor.lastrowid, "message": "Curso salvo com sucesso!"}, status.HTTP_201_CREATED
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/courses/{course_id}")
def update_course_progress(course_id: int, course_data: CourseUpdate):
    completed = 1 if course_data.progress >= 100 else 0
    """Atualiza o progresso de um curso existente.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
            course = cursor.fetchone()
            if course is None:
                raise HTTPException(status_code=404, detail="Curso não encontrado.")
            cursor.execute("""
                UPDATE courses
                SET progress = ?, completed = ?
                WHERE id = ?
            """, (course_data.progress, completed, course_id))
            conn.commit()
            return {"message": "Progresso do curso atualizado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
