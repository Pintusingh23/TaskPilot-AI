import React, { useState, useEffect } from 'react';
import api from '../api/client';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import {
  User,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Database,
  Cpu,
  Mail,
  Calendar,
  Sparkles,
  Search
} from 'lucide-react';

export default function SettingsPage() {
  const { user } = useAuth();
  const [integrations, setIntegrations] = useState(null);
  const [apiHealth, setApiHealth] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [intRes, healthRes] = await Promise.allSettled([
          api.get('/gmail/status'),
          api.get('/health')
        ]);
        if (intRes.status === 'fulfilled') setIntegrations(intRes.value.data);
        if (healthRes.status === 'fulfilled') setApiHealth(healthRes.value.data);
      } catch (err) {
        console.error('Error fetching settings status:', err);
      }
    };
    fetchStatus();
  }, []);

  return (
    <div className="flex-1 flex flex-col h-screen overflow-y-auto bg-slate-50 dark:bg-slate-950">
      <Navbar
        title="Settings & Integrations"
        subtitle="Manage user account and view connected external AI & Google services"
      />

      <main className="p-8 space-y-8 max-w-4xl mx-auto w-full">
        {/* User Profile Card */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white text-xl font-bold shadow-md shadow-brand-500/20">
              {user?.name ? user.name[0].toUpperCase() : 'U'}
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-900 dark:text-white">{user?.name}</h3>
              <p className="text-xs text-slate-400">{user?.email}</p>
              <div className="inline-flex items-center gap-1.5 mt-1 px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 text-[11px] font-semibold">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>JWT Authenticated</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-slate-400">User ID</span>
              <p className="font-mono font-semibold text-slate-700 dark:text-slate-300 mt-0.5">#{user?.id}</p>
            </div>
            <div>
              <span className="text-slate-400">Member Since</span>
              <p className="font-semibold text-slate-700 dark:text-slate-300 mt-0.5">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Active'}
              </p>
            </div>
          </div>
        </div>

        {/* Connected Services & Integrations */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm space-y-5">
          <div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-brand-500" />
              <span>Connected AI & Productivity Integrations</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">Live status of backend tools and OAuth configurations</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Groq LLM */}
            <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2 font-bold text-sm text-slate-800 dark:text-slate-200">
                  <Sparkles className="w-4 h-4 text-brand-500" />
                  <span>Groq AI Agent</span>
                </div>
                <p className="text-xs text-slate-400 font-mono">openai/gpt-oss-20b</p>
                <p className="text-[11px] text-slate-500">Fast inference & tool calling enabled</p>
              </div>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full">
                <CheckCircle2 className="w-3 h-3" />
                Active
              </span>
            </div>

            {/* Tavily Search */}
            <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2 font-bold text-sm text-slate-800 dark:text-slate-200">
                  <Search className="w-4 h-4 text-indigo-500" />
                  <span>Tavily Web Search</span>
                </div>
                <p className="text-xs text-slate-400">Live internet search tool</p>
                <p className="text-[11px] text-slate-500">API Key configured in environment</p>
              </div>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full">
                <CheckCircle2 className="w-3 h-3" />
                Active
              </span>
            </div>

            {/* Google Calendar */}
            <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2 font-bold text-sm text-slate-800 dark:text-slate-200">
                  <Calendar className="w-4 h-4 text-emerald-500" />
                  <span>Google Calendar API</span>
                </div>
                <p className="text-xs text-slate-400">OAuth 2.0 calendar scope</p>
                <p className="text-[11px] text-slate-500">
                  {integrations?.calendar?.token_exists ? 'calendar_token.json loaded' : 'Token pending'}
                </p>
              </div>
              <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                integrations?.calendar?.token_exists
                  ? 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40'
                  : 'text-amber-600 bg-amber-50 dark:bg-amber-950/40'
              }`}>
                {integrations?.calendar?.token_exists ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                {integrations?.calendar?.token_exists ? 'Synced' : 'Offline'}
              </span>
            </div>

            {/* Gmail */}
            <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2 font-bold text-sm text-slate-800 dark:text-slate-200">
                  <Mail className="w-4 h-4 text-rose-500" />
                  <span>Gmail API</span>
                </div>
                <p className="text-xs text-slate-400">OAuth 2.0 inbox & send scopes</p>
                <p className="text-[11px] text-slate-500">
                  {integrations?.gmail?.token_exists ? 'token.json loaded' : 'Token pending'}
                </p>
              </div>
              <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                integrations?.gmail?.token_exists
                  ? 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40'
                  : 'text-amber-600 bg-amber-50 dark:bg-amber-950/40'
              }`}>
                {integrations?.gmail?.token_exists ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                {integrations?.gmail?.token_exists ? 'Synced' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

