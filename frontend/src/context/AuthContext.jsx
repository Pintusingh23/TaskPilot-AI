import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext();

const DEFAULT_USER = {
  name: "Pintu Singh",
  email: "pintu@taskpilot.ai",
  password: "password123"
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('taskpilot_token'));
  const [loading, setLoading] = useState(true);

  const autoAuthenticate = async () => {
    try {
      // 1. Try to fetch user with current token
      const storedToken = localStorage.getItem('taskpilot_token');
      if (storedToken) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
          setLoading(false);
          return;
        } catch {
          localStorage.removeItem('taskpilot_token');
        }
      }

      // 2. Try auto-login
      try {
        const loginRes = await api.post('/auth/login', {
          email: DEFAULT_USER.email,
          password: DEFAULT_USER.password
        });
        const { access_token, user: userData } = loginRes.data;
        localStorage.setItem('taskpilot_token', access_token);
        setToken(access_token);
        setUser(userData);
      } catch {
        // 3. If login failed, auto-register
        const regRes = await api.post('/auth/register', DEFAULT_USER);
        const { access_token, user: userData } = regRes.data;
        localStorage.setItem('taskpilot_token', access_token);
        setToken(access_token);
        setUser(userData);
      }
    } catch (err) {
      console.error('Auto authentication error:', err);
      // Fallback local user so UI is always accessible
      setUser({ name: DEFAULT_USER.name, email: DEFAULT_USER.email, id: 1 });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    autoAuthenticate();
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('taskpilot_token', access_token);
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const register = async (name, email, password) => {
    const res = await api.post('/auth/register', { name, email, password });
    const { access_token, user: userData } = res.data;
    localStorage.setItem('taskpilot_token', access_token);
    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const logout = () => {
    // Reset back to auto authenticated user
    autoAuthenticate();
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, isAuthenticated: true, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
