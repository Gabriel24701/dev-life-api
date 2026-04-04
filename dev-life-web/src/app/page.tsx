"use client";

import { useEffect, useState } from "react";
import { api } from "../services/api";


interface Task {
  id: number;
  title: string;
  category: string;
  description: string;
  created_at: string;
}

interface Course {
  id: number;
  title: string;
  platform: string;
  progress: number;
  start_date: string;
}

interface Habit {
  id: number;
  name: string;
  category: string;
  goal_type: string;
  target: number;
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);

  const loadData = async () => {
    try {
      const [t, c, h] = await Promise.all([
        api.getTasks(), api.getCourses(), api.getHabits()
      ]);
      setTasks(t);
      setCourses(c);
      setHabits(h);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    api.getTasks().then(setTasks).catch(console.error);
    api.getCourses().then(setCourses).catch(console.error);
    api.getHabits().then(setHabits).catch(console.error);
  }, []);

  const handleConcludeTask = async (id: number) => {
    await api.concludeTask(id);
    loadData();
  };

  return (
    <main className="min-h-screen bg-gray-900 text-gray-100 p-8">
      <header className="mb-10">
        <h1 className="text-4xl font-bold text-blue-400">🚀 Dev Life Dashboard</h1>
        <p className="text-gray-400 mt-2">Visão geral da sua produtividade e estudos.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Coluna de Tarefas */}
        <section className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <h2 className="text-2xl font-semibold mb-4 text-white border-b border-gray-700 pb-2">📝 Tarefas</h2>
          <div className="space-y-4">
            {tasks.map((task: Task, index: number) => (
              <div key={index} className="bg-gray-700 p-4 rounded-lg flex justify-between items-center">
                <div>
                  <h3 className="font-medium">{task.title}</h3>
                  <span className="text-xs bg-blue-900 text-blue-200 px-2 py-1 rounded-full">{task.category}</span>
                </div>
                <button 
                  onClick={() => handleConcludeTask(task.id)}
                  className="bg-green-600 hover:bg-green-500 text-white px-3 py-1 rounded text-sm transition-colors"
                >
                  Concluir
                </button>
              </div>
            ))}
            {tasks.length === 0 && <p className="text-gray-500 text-sm">Nenhuma tarefa pendente.</p>}
          </div>
        </section>

        {/* Coluna de Cursos */}
        <section className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <h2 className="text-2xl font-semibold mb-4 text-white border-b border-gray-700 pb-2">📘 Cursos</h2>
          <div className="space-y-4">
            {courses.map((course: Course, index: number) => (
              <div key={index} className="bg-gray-700 p-4 rounded-lg">
                <h3 className="font-medium">{course.title}</h3>
                <div className="w-full bg-gray-600 rounded-full h-2.5 mt-3">
                  <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: `${course.progress}%` }}></div>
                </div>
                <p className="text-xs text-gray-400 mt-1">{course.progress}% concluído em {course.platform}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Coluna de Hábitos */}
        <section className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <h2 className="text-2xl font-semibold mb-4 text-white border-b border-gray-700 pb-2">🔁 Hábitos</h2>
          <div className="space-y-4">
            {habits.map((habit: Habit, index: number) => (
              <div key={index} className="bg-gray-700 p-4 rounded-lg flex justify-between items-center">
                <h3 className="font-medium">{habit.name}</h3>
                <span className="text-xs text-gray-300">Meta: {habit.target}x {habit.goal_type}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}