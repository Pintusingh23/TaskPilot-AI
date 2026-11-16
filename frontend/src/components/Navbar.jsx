import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Sparkles, Plus, Palette, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Navbar({ title, subtitle, onActionClick, actionLabel }) {
  const { user } = useAuth();
  const { currentPalette, accentColor, setAccentColor, palettes } = useTheme();
  const navigate = useNavigate();
  const [showColorPicker, setShowColorPicker] = useState(false);

  return (
    <header className={`h-16 px-8 bg-gradient-to-r ${currentPalette.navGradient} text-white shadow-md flex items-center justify-between sticky top-0 z-20 transition-all duration-300`}>
      {/* Title & Subtitle */}
      <div>
        <h2 className="text-xl font-bold tracking-tight text-white leading-tight drop-shadow-sm">{title}</h2>
        {subtitle && <p className="text-xs text-white/80 font-medium">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Color Palette Switcher */}
        <div className="relative">
          <button
            onClick={() => setShowColorPicker(!showColorPicker)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-md text-white text-xs font-semibold border border-white/25 shadow-sm transition-all"
            title="Choose Theme Color"
          >
            <Palette className="w-3.5 h-3.5" />
            <span className="capitalize hidden sm:inline">{currentPalette.name.split(' ')[0]}</span>
            <span className="w-2.5 h-2.5 rounded-full bg-white shadow-sm ml-1" />
          </button>

          {/* Color Picker Dropdown */}
          {showColorPicker && (
            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-xl p-2 z-50 animate-in fade-in zoom-in-95">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-2 py-1">Select Theme Color</p>
              <div className="space-y-1">
                {Object.values(palettes).map((p) => (
                  <button
                    key={p.id}
                    onClick={() => {
                      setAccentColor(p.id);
                      setShowColorPicker(false);
                    }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                      accentColor === p.id
                        ? 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`w-3.5 h-3.5 rounded-full ${p.accentDot}`} />
                      <span>{p.name}</span>
                    </div>
                    {accentColor === p.id && <Check className="w-3.5 h-3.5 text-emerald-500" />}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Action Button */}
        {actionLabel && (
          <button
            onClick={onActionClick}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-white text-slate-900 hover:bg-white/90 text-sm font-bold shadow-md shadow-black/10 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-4 h-4 text-slate-900" />
            <span>{actionLabel}</span>
          </button>
        )}

        {/* Ask AI Button */}
        <button
          onClick={() => navigate('/chat')}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-md text-white text-sm font-medium border border-white/25 transition-all"
        >
          <Sparkles className="w-4 h-4 text-white" />
          <span className="hidden sm:inline">Ask AI</span>
        </button>
      </div>
    </header>
  );
}
