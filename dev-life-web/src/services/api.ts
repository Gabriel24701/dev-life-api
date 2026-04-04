const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const api = {
  // Tasks
  getTasks: async () => {
    const res = await fetch(`${API_URL}/tasks`);
    return res.json();
  },
  concludeTask: async (id: number) => {
    await fetch(`${API_URL}/tasks/${id}`, { method: 'PATCH' });
  },
  
  // Courses
  getCourses: async () => {
    const res = await fetch(`${API_URL}/courses`);
    return res.json();
  },
  
  // Habits
  getHabits: async () => {
    const res = await fetch(`${API_URL}/habits`);
    return res.json();
  }
};