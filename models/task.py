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
            f"Tarefa: {self._title}\n"
            f"Categoria: {self._category}\n"
            f"Descrição: {self._description}\n"
            f"Status: {status}\n"
            f"Criada em: {self._created_at}"
        )
    
    def concluir_tarefa(self):
        self._status = True

    @property
    def altera_status_tarefa(self):
        return '✅' if self._status else '❎'
    
    def to_dict(self):
        return {
            "title": self._title,
            "category": self._category,
            "description": self._description,
            "status": self._status,
            "created_at": self._created_at
        }