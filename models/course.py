class Course:
    def __init__(self, title, platform, progress, start_date):
        self._title = title
        self._platform = platform
        self._progress = progress
        self._start_date = start_date
        self._completed = False

    def to_dict(self):
        return (
            f"Curso: {self._title}\n"
            f"Plataforma: {self._platform}\n"
            f"Progresso: {self._progress}%\n"
            f"Iniciado em: {self._start_date}\n"
            f"Concluído: {'✅' if self._completed else '❎'}"
        )
    
    def __str__(self):
        status = '✅' if self._completed else '❎'
        return f"{self._title} on {self._platform} - {self._progress}% {status}"
        
    def update_course(self, value):
        self._progress = min(value, 100)
        if self._progress == 100:
            self._completed = True
    