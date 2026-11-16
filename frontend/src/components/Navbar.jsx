import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Bell, Sparkles, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Navbar({ title, subtitle, onActionClick, actionLabel }) {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="h-16 px-8 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-20">
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white leading-tight">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {actionLabel && (
          <button
            onClick={onActionClick}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium shadow-sm shadow-brand-500/20 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-4 h-4" />
            <span>{actionLabel}</span>
          </button>
        )}

        <button
          onClick={() => navigate('/chat')}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 text-sm font-medium transition-colors"
        >
          <Sparkles className="w-4 h-4 text-brand-500" />
          <span>Ask AI</span>
        </button>
      </div>
    </header>
  );
}

