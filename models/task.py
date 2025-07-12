from pydantic import BaseModel

class Task:
    def __init__(self, title, category, description, created_at):
        self._title = title
        self._category = category
        self._description = description
        self._status = False
        self._created_at = created_at

    def __str__(self):
        status = '✅' if self._status else '❎'
        return (
            f"Task: {self._title}\n"
            f"Category: {self._category}\n"
            f"Description: {self._description}\n"
            f"Status: {status}\n"
            f"Created at: {self._created_at}"
        )
    
    def to_dict(self):
        return {
            "title": self._title,
            "category": self._category,
            "description": self._description,
            "status": self._status,
            "created_at": self._created_at
        }
    
    def complete_task(self):
        self._status = True


class TaskCreate(BaseModel):
    title: str
    category: str
    description: str
    created_at: str
