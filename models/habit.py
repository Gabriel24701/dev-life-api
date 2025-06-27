from datetime import date

class Habit:
    def __init__(self, name, category, goal_type, target, created_at):
        self._name = name                    
        self._category = category
        self._goal_type = goal_type          
        self._target = target                
        self._created_at = created_at        
        self._log = []                       
  

    def __str__(self):
        return f"{self._name} ({self._category}) - {self._goal_type}, alvo: {self._target}x | Criado em: {self._created_at}"


    def to_dict(self):
        return {
            "name": self._name,
            "category": self._category,
            "goal_type": self._goal_type,
            "target": self._target,
            "created_at": self._created_at,
            "log": self._log,
            "streak": self.get_streak()
        }


    def mark_today(self):
        today = date.today().isoformat()
        if today not in self._log:
            self._log.append(today)

    def get_total_checkins(self):
        return len(self._log)
    
    def get_streak(self):
        today = date.today()
        streak = 0
        days = [date.fromisoformat(d) for d in self._log]
        days.sort(reverse=True)

        for i, day in enumerate(days):
            if i == 0 and (today - day).days > 1:
                break
            elif i > 0 and (days[i-1] - day).days != 1:
                break
            streak += 1

        return streak