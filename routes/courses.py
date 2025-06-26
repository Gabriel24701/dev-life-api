from fastapi import APIRouter
from models.course import Course

router = APIRouter()

courses = []

@router.get("/courses")
def get_courses():
    return [course.to_dict() for course in courses]

@router.post("/courses")
def create_course(title: str, platform: str, progress: int, start_date: str):
    new_course = Course(title, platform, progress, start_date)
    courses.append(new_course)
    return {"message": "Curso criado com sucesso!"}

@router.patch("/courses/{course_id}")
def update_course_progress(course_id: int, progress: int):
    if 0 <= course_id < len(courses):
        courses[course_id].update_course(progress)
        return {"message": "Progresso do curso atualizado com sucesso."}
    return {"error": "Curso não encontrado."}