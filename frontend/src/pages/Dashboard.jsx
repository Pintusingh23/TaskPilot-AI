import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import Navbar from '../components/Navbar';
import TaskModal from '../components/TaskModal';
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  ListTodo,
  Calendar,
  Sparkles,
  ArrowRight,
  Plus,
  Check,
  ChevronRight
} from 'lucide-react';

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      setLoading(true);
      const [tasksRes, calRes] = await Promise.allSettled([
        api.get('/tasks'),
        api.get('/calendar/events?max_results=5')
      ]);

      if (tasksRes.status === 'fulfilled') {
        setTasks(tasksRes.value.data || []);
      }
      if (calRes.status === 'fulfilled') {
        setCalendarEvents(calRes.value.data?.events || []);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateTask = async (taskData) => {
    await api.post('/tasks', taskData);
    fetchData();
  };

  const handleToggleComplete = async (taskId) => {
    try {
      await api.patch(`/tasks/${taskId}/complete`);
      setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: 'completed' } : t));
    } catch (err) {
      console.error('Failed to complete task:', err);
    }
  };

  // Metrics
  const totalTasks = tasks.length;
  const pendingTasks = tasks.filter(t => t.status === 'pending').length;
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress').length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const highPriority = tasks.filter(t => t.priority === 'high' && t.status !== 'completed').length;

  return (
    <div className="flex-1 flex flex-col h-screen overflow-y-auto bg-slate-50 dark:bg-slate-950">
      <Navbar
        title="Dashboard"
        subtitle="Overview of your productivity and upcoming events"
        actionLabel="New Task"
        onActionClick={() => setIsModalOpen(true)}
      />

      <main className="p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Total Tasks</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{totalTasks}</h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400 flex items-center justify-center">
              <ListTodo className="w-6 h-6" />
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Pending</p>
              <h3 className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">{pendingTasks}</h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center">
              <Clock className="w-6 h-6" />
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Completed</p>
              <h3 className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{completedTasks}</h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">High Priority</p>
              <h3 className="text-2xl font-bold text-rose-600 dark:text-rose-400 mt-1">{highPriority}</h3>
            </div>
            <div className="w-12 h-12 rounded-xl bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Quick AI Action Banner */}
        <div className="p-6 rounded-3xl bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-600 text-white shadow-lg shadow-brand-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 font-semibold text-brand-100 text-sm">
              <Sparkles className="w-4 h-4" />
              <span>AI Productivity Assistant</span>
            </div>
            <h2 className="text-xl font-bold">Ask TaskPilot to schedule meetings, summarize tasks, or search info</h2>
            <p className="text-xs text-brand-100/90">Powered by Groq LLM with Gmail and Google Calendar tools</p>
          </div>
          <button
            onClick={() => navigate('/chat')}
            className="px-5 py-2.5 rounded-xl bg-white text-brand-600 font-bold text-sm shadow-md hover:bg-brand-50 transition-all flex items-center gap-2 shrink-0 hover:scale-105"
          >
            <span>Open AI Chat</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Two-column layout: Recent Tasks & Upcoming Calendar */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Tasks */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-lg text-slate-900 dark:text-white flex items-center gap-2">
                <ListTodo className="w-5 h-5 text-brand-500" />
                <span>Recent Tasks</span>
              </h3>
              <button
                onClick={() => navigate('/tasks')}
                className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
              >
                <span>View all</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden divide-y divide-slate-100 dark:divide-slate-800">
              {tasks.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-sm">
                  No tasks found. Click "New Task" or ask TaskPilot AI to create one!
                </div>
              ) : (
                tasks.slice(0, 5).map((task) => (
                  <div key={task.id} className="p-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleToggleComplete(task.id)}
                        className={`w-6 h-6 rounded-lg border flex items-center justify-center transition-colors ${
                          task.status === 'completed'
                            ? 'bg-emerald-500 border-emerald-500 text-white'
                            : 'border-slate-300 dark:border-slate-600 hover:border-brand-500'
                        }`}
                      >
                        {task.status === 'completed' && <Check className="w-3.5 h-3.5" />}
                      </button>
                      <div>
                        <h4 className={`text-sm font-semibold ${task.status === 'completed' ? 'line-through text-slate-400 dark:text-slate-500' : 'text-slate-800 dark:text-slate-200'}`}>
                          {task.title}
                        </h4>
                        {task.description && (
                          <p className="text-xs text-slate-400 line-clamp-1">{task.description}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                        task.priority === 'high'
                          ? 'bg-rose-50 text-rose-600 dark:bg-rose-950/40 dark:text-rose-400'
                          : task.priority === 'medium'
                          ? 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400'
                          : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
                      }`}>
                        {task.priority}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Upcoming Calendar Events */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-lg text-slate-900 dark:text-white flex items-center gap-2">
                <Calendar className="w-5 h-5 text-emerald-500" />
                <span>Google Calendar</span>
              </h3>
              <button
                onClick={() => navigate('/calendar')}
                className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
              >
                <span>Full view</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm p-4 space-y-3">
              {calendarEvents.length === 0 ? (
                <div className="p-6 text-center text-slate-400 text-xs">
                  No upcoming Google Calendar events found or calendar not synced.
                </div>
              ) : (
                calendarEvents.slice(0, 4).map((event, idx) => (
                  <div key={idx} className="p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 space-y-1">
                    <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">{event.title}</p>
                    <p className="text-[11px] text-slate-400">
                      {event.start ? new Date(event.start).toLocaleString() : 'Time unspecified'}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>

      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleCreateTask}
      />
    </div>
  );
}

