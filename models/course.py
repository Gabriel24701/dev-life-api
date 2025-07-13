from pydantic import BaseModel

class Course:
    def __init__(self, title, platform, progress, start_date):
        self._title = title
        self._platform = platform
        self._progress = progress
        self._start_date = start_date
        self._completed = progress >= 100

    def __str__(self):
        status = '✅' if self._completed else '❎'
        return f"{self._title} on {self._platform} - {self._progress}% {status}"
    
    def to_dict(self):
        return {
            "title": self._title,
            "platform": self._platform,
            "progress": self._progress,
            "start_date": self._start_date,
            "completed": self._completed
        }
    
    def update_progress(self, value):
        self._progress = min(value, 100)
        if self._progress == 100:
            self._completed = True

            from pydantic import BaseModel

class CourseCreate(BaseModel):
    title: str
    platform: str
    progress: int
    start_date: str

class CourseUpdate(BaseModel):
    progress: int