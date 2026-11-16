import React, { useState, useEffect, useRef } from 'react';
import api from '../api/client';
import Navbar from '../components/Navbar';
import ActionPreviewCard from '../components/ActionPreviewCard';
import {
  Send,
  Sparkles,
  Bot,
  User,
  Plus,
  Trash2,
  Wrench,
  CheckCircle,
  AlertCircle,
  Calendar,
  Mail,
  Search,
  Calculator,
  ListTodo
} from 'lucide-react';

export default function Chat() {
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const [isConfirming, setIsConfirming] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (activeConvId) {
      fetchMessages(activeConvId);
    } else {
      setMessages([]);
    }
  }, [activeConvId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, pendingAction]);

  const fetchConversations = async () => {
    try {
      const res = await api.get('/conversations');
      setConversations(res.data || []);
      if (res.data?.length > 0 && !activeConvId) {
        setActiveConvId(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const fetchMessages = async (convId) => {
    try {
      const res = await api.get(`/conversations/${convId}`);
      setMessages(res.data?.messages || []);
      setPendingAction(null);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleStartNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    setPendingAction(null);
  };

  const handleDeleteConversation = async (convId, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this conversation?')) return;
    try {
      await api.delete(`/conversations/${convId}`);
      setConversations(prev => prev.filter(c => c.id !== convId));
      if (activeConvId === convId) {
        handleStartNewChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSendMessage = async (textToSend = null) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || loading) return;

    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInputMessage('');
    setLoading(true);
    setPendingAction(null);

    try {
      const res = await api.post('/chat', {
        message: text,
        conversation_id: activeConvId
      });

      const { response: aiResponse, conversation_id: newConvId, tool_calls, action_preview } = res.data;

      if (!activeConvId && newConvId) {
        setActiveConvId(newConvId);
        fetchConversations();
      }

      const assistantMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: aiResponse,
        tool_calls: tool_calls || [],
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMsg]);

      if (action_preview) {
        setPendingAction(action_preview);
      }
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Error: ${err.response?.data?.detail || err.message || 'Something went wrong.'}`,
        isError: true,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmAction = async () => {
    if (!pendingAction) return;
    setIsConfirming(true);
    const actionName = pendingAction.action;
    // Send confirmation statement to AI
    const confirmationText = `Yes, please proceed and execute the ${actionName}. I confirm.`;
    setPendingAction(null);
    setIsConfirming(false);
    await handleSendMessage(confirmationText);
  };

  const handleCancelAction = () => {
    setPendingAction(null);
    setMessages(prev => [
      ...prev,
      {
        id: Date.now(),
        role: 'assistant',
        content: 'Action cancelled. Nothing was executed.',
        created_at: new Date().toISOString()
      }
    ]);
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
      <Navbar
        title="AI Assistant"
        subtitle="Conversational assistant with tool execution & memory"
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Conversations Sidebar */}
        <div className="w-72 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 flex flex-col shrink-0">
          <div className="p-4 border-b border-slate-100 dark:border-slate-800">
            <button
              onClick={handleStartNewChat}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-brand-500 hover:bg-brand-600 text-white font-semibold text-xs shadow-sm shadow-brand-500/20 transition-all hover:scale-[1.01]"
            >
              <Plus className="w-4 h-4" />
              <span>New Conversation</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            {conversations.length === 0 ? (
              <p className="text-center text-slate-400 text-xs py-8">No previous chats</p>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => setActiveConvId(conv.id)}
                  className={`group flex items-center justify-between p-3 rounded-xl cursor-pointer text-xs transition-colors ${
                    activeConvId === conv.id
                      ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-700 dark:text-brand-300 font-semibold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60'
                  }`}
                >
                  <span className="truncate pr-2">{conv.title}</span>
                  <button
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 transition-opacity"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Main Window */}
        <div className="flex-1 flex flex-col bg-slate-50 dark:bg-slate-950 overflow-hidden">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 max-w-lg mx-auto space-y-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-xl shadow-brand-500/20">
                  <Sparkles className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-slate-800 dark:text-white">How can TaskPilot help you today?</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  I can manage your tasks, check your Google Calendar, read inbox emails, search the web, and calculate math.
                </p>

                {/* Quick Prompts */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full mt-4">
                  {[
                    "Create a task to finish the project tomorrow",
                    "Show my pending tasks",
                    "Check my upcoming calendar events",
                    "Read recent emails from my inbox"
                  ].map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(prompt)}
                      className="p-3 text-left rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-brand-500 hover:shadow-sm text-xs text-slate-700 dark:text-slate-300 font-medium transition-all"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
                >
                  <div
                    className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold shrink-0 ${
                      isUser
                        ? 'bg-slate-900 text-white dark:bg-slate-700'
                        : 'bg-brand-500 text-white shadow-sm shadow-brand-500/30'
                    }`}
                  >
                    {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  <div className="space-y-2 max-w-2xl">
                    {/* Tool call badges */}
                    {msg.tool_calls && msg.tool_calls.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mb-1.5">
                        {msg.tool_calls.map((tc, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-200 dark:bg-slate-800 text-[11px] font-mono text-slate-700 dark:text-slate-300"
                          >
                            <Wrench className="w-3 h-3 text-brand-500" />
                            <span>{tc.tool}</span>
                          </span>
                        ))}
                      </div>
                    )}

                    <div
                      className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                        isUser
                          ? 'bg-brand-500 text-white rounded-tr-none shadow-sm shadow-brand-500/20'
                          : msg.isError
                          ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-900 rounded-tl-none'
                          : 'bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-800 rounded-tl-none shadow-sm'
                      }`}
                    >
                      {msg.content}
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Pending Action Confirmation Card */}
            {pendingAction && (
              <div className="max-w-2xl mx-auto">
                <ActionPreviewCard
                  action={pendingAction.action}
                  preview={pendingAction.preview}
                  onConfirm={handleConfirmAction}
                  onCancel={handleCancelAction}
                  isConfirming={isConfirming}
                />
              </div>
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="flex gap-3 max-w-3xl mr-auto">
                <div className="w-8 h-8 rounded-xl bg-brand-500 text-white flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-tl-none flex items-center gap-2 text-xs text-slate-500 font-medium">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 rounded-full bg-brand-500 animate-bounce"></span>
                    <span className="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:0.2s]"></span>
                    <span className="w-2 h-2 rounded-full bg-brand-500 animate-bounce [animation-delay:0.4s]"></span>
                  </div>
                  <span>TaskPilot is thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Bar */}
          <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="max-w-4xl mx-auto flex items-center gap-3"
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask TaskPilot to create a task, check calendar, send email..."
                disabled={loading}
                className="flex-1 px-4 py-3 rounded-2xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 transition-colors disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || loading}
                className="p-3 rounded-2xl bg-brand-500 hover:bg-brand-600 text-white shadow-md shadow-brand-500/20 disabled:opacity-50 transition-all hover:scale-105 active:scale-95"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

