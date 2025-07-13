from fastapi import APIRouter
from models.course import Course
from models.course import CourseCreate, CourseUpdate
import sqlite3

router = APIRouter()

courses = []

@router.get("/courses")
def get_courses():
    conn = sqlite3.connect("database/devlife.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, platform, progress, start_date, completed FROM courses")
    rows = cursor.fetchall()
    courses = []
    for row in rows:
        course = {
            "id": row[0],
            "title": row[1],
            "platform": row[2],
            "progress": row[3],
            "start_date": row[4],
            "completed": row[5] == 1
        }
        courses.append(course)
    conn.close()
    return courses

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
def update_course_progress(course_id: int, course_data: CourseUpdate):
    completed = 1 if course_data.progress >= 100 else 0
    conn = sqlite3.connect("database/devlife.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    if course is None:
        conn.close()
        return {"error": "Curso não encontrado."}
    cursor.execute("""
        UPDATE courses
        SET progress = ?, completed = ?
        WHERE id = ?
    """, (course_data.progress, completed, course_id))
    conn.commit()
    conn.close()
    return {"message": "Progresso do curso atualizado com sucesso."}
