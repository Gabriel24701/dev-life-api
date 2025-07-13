from fastapi import APIRouter
from models.course import Course
from models.course import CourseCreate
import sqlite3

router = APIRouter()

courses = []

@router.get("/courses")
def get_courses():
    return [course.to_dict() for course in courses]

@router.post("/courses")
def create_course(course: CourseCreate):
    completed = 1 if course.progress >= 100 else 0
    conn = sqlite3.connect("database/devlife.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO courses (title, platform, progress, start_date, completed)
        VALUES (?, ?, ?, ?, ?)
    """, (course.title, course.platform, course.progress, course.start_date, completed))
    conn.commit()
    conn.close()
    return {"message": "Curso criado com sucesso!"}


@router.patch("/courses/{course_id}")
def update_course_progress(course_id: int, progress: int):
    if 0 <= course_id < len(courses):
        courses[course_id].update_course(progress)
        return {"message": "Progresso do curso atualizado com sucesso."}
    return {"error": "Curso não encontrado."}