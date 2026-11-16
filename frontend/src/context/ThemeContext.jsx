import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const ACCENT_PALETTES = {
  red: {
    id: 'red',
    name: 'Crimson Red',
    navGradient: 'from-red-600 via-rose-600 to-red-700',
    primaryBg: 'bg-red-600 hover:bg-red-700',
    activeNav: 'bg-red-600 text-white shadow-red-500/30',
    text: 'text-red-600 dark:text-red-400',
    border: 'border-red-500',
    ring: 'focus:ring-red-500',
    badge: 'bg-red-50 text-red-600 dark:bg-red-950/40 dark:text-red-400',
    accentDot: 'bg-red-500',
  },
  purple: {
    id: 'purple',
    name: 'Electric Purple',
    navGradient: 'from-purple-600 via-indigo-600 to-purple-700',
    primaryBg: 'bg-purple-600 hover:bg-purple-700',
    activeNav: 'bg-purple-600 text-white shadow-purple-500/30',
    text: 'text-purple-600 dark:text-purple-400',
    border: 'border-purple-500',
    ring: 'focus:ring-purple-500',
    badge: 'bg-purple-50 text-purple-600 dark:bg-purple-950/40 dark:text-purple-400',
    accentDot: 'bg-purple-500',
  },
  blue: {
    id: 'blue',
    name: 'Ocean Blue',
    navGradient: 'from-blue-600 via-sky-600 to-blue-700',
    primaryBg: 'bg-blue-600 hover:bg-blue-700',
    activeNav: 'bg-blue-600 text-white shadow-blue-500/30',
    text: 'text-blue-600 dark:text-blue-400',
    border: 'border-blue-500',
    ring: 'focus:ring-blue-500',
    badge: 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400',
    accentDot: 'bg-blue-500',
  },
  emerald: {
    id: 'emerald',
    name: 'Emerald Green',
    navGradient: 'from-emerald-600 via-teal-600 to-emerald-700',
    primaryBg: 'bg-emerald-600 hover:bg-emerald-700',
    activeNav: 'bg-emerald-600 text-white shadow-emerald-500/30',
    text: 'text-emerald-600 dark:text-emerald-400',
    border: 'border-emerald-500',
    ring: 'focus:ring-emerald-500',
    badge: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400',
    accentDot: 'bg-emerald-500',
  },
  amber: {
    id: 'amber',
    name: 'Sunset Amber',
    navGradient: 'from-amber-600 via-orange-600 to-amber-700',
    primaryBg: 'bg-amber-600 hover:bg-amber-700',
    activeNav: 'bg-amber-600 text-white shadow-amber-500/30',
    text: 'text-amber-600 dark:text-amber-400',
    border: 'border-amber-500',
    ring: 'focus:ring-amber-500',
    badge: 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400',
    accentDot: 'bg-amber-500',
  }
};

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('taskpilot_theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Default accent color is Red as requested
  const [accentColor, setAccentColor] = useState(() => {
    const savedColor = localStorage.getItem('taskpilot_accent_color');
    return savedColor && ACCENT_PALETTES[savedColor] ? savedColor : 'red';
  });

  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
      localStorage.setItem('taskpilot_theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('taskpilot_theme', 'light');
    }
  }, [darkMode]);

  const changeAccentColor = (colorKey) => {
    if (ACCENT_PALETTES[colorKey]) {
      setAccentColor(colorKey);
      localStorage.setItem('taskpilot_accent_color', colorKey);
    }
  };

  const toggleTheme = () => setDarkMode(prev => !prev);

  const currentPalette = ACCENT_PALETTES[accentColor] || ACCENT_PALETTES.red;

  return (
    <ThemeContext.Provider value={{
      darkMode,
      toggleTheme,
      accentColor,
      setAccentColor: changeAccentColor,
      currentPalette,
      palettes: ACCENT_PALETTES
    }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
