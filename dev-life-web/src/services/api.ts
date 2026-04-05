const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const api = {
  getTasks: async () => {
    const res = await fetch(`${API_URL}/tasks`, { cache: 'no-store' });
    return res.json();
  },
  concludeTask: async (id: number) => {
    await fetch(`${API_URL}/tasks/${id}`, { method: 'PATCH' });
  },
  
  getCourses: async () => {
    const res = await fetch(`${API_URL}/courses`, { cache: 'no-store' });
    return res.json();
  },
  
  getHabits: async () => {
    const res = await fetch(`${API_URL}/habits`, { cache: 'no-store' });
    return res.json();
  }
};