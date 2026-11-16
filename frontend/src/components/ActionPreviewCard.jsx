import React from 'react';
import { Mail, Calendar, Trash2, AlertTriangle, Check, X } from 'lucide-react';

export default function ActionPreviewCard({ action, preview, onConfirm, onCancel, isConfirming }) {
  if (!preview) return null;

  return (
    <div className="my-3 p-4 rounded-2xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/70 dark:bg-amber-950/20 backdrop-blur-sm text-slate-800 dark:text-slate-200 max-w-lg shadow-sm">
      <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-semibold text-sm mb-3">
        <AlertTriangle className="w-4 h-4 shrink-0" />
        <span>Action Confirmation Required</span>
      </div>

      {/* Action-specific visual preview */}
      {action === 'send_email' && (
        <div className="space-y-1.5 text-xs bg-white/80 dark:bg-slate-900/80 p-3 rounded-xl border border-amber-100 dark:border-amber-900/40">
          <div className="flex items-center gap-2 text-slate-500 font-medium">
            <Mail className="w-3.5 h-3.5 text-brand-500" />
            <span>Send Email</span>
          </div>
          <p><span className="font-semibold text-slate-600 dark:text-slate-400">To:</span> {preview.recipient}</p>
          <p><span className="font-semibold text-slate-600 dark:text-slate-400">Subject:</span> {preview.subject}</p>
          <div className="mt-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-slate-700 dark:text-slate-300 italic whitespace-pre-wrap">
            "{preview.body}"
          </div>
        </div>
      )}

      {action === 'create_calendar_event' && (
        <div className="space-y-1.5 text-xs bg-white/80 dark:bg-slate-900/80 p-3 rounded-xl border border-amber-100 dark:border-amber-900/40">
          <div className="flex items-center gap-2 text-slate-500 font-medium">
            <Calendar className="w-3.5 h-3.5 text-emerald-500" />
            <span>Schedule Calendar Event</span>
          </div>
          <p><span className="font-semibold text-slate-600 dark:text-slate-400">Event:</span> {preview.summary}</p>
          <p><span className="font-semibold text-slate-600 dark:text-slate-400">Start:</span> {preview.start}</p>
          <p><span className="font-semibold text-slate-600 dark:text-slate-400">End:</span> {preview.end}</p>
          {preview.description && (
            <p><span className="font-semibold text-slate-600 dark:text-slate-400">Description:</span> {preview.description}</p>
          )}
        </div>
      )}

      {action === 'delete_task' && (
        <div className="space-y-1.5 text-xs bg-white/80 dark:bg-slate-900/80 p-3 rounded-xl border border-amber-100 dark:border-amber-900/40">
          <div className="flex items-center gap-2 text-rose-500 font-medium">
            <Trash2 className="w-3.5 h-3.5" />
            <span>Delete Task</span>
          </div>
          <p><span className="font-semibold text-slate-600 dark:text-slate-400">Task Title:</span> {preview.title}</p>
          <p className="text-[11px] text-rose-600 dark:text-rose-400">Warning: This operation cannot be undone.</p>
        </div>
      )}

      {/* Buttons */}
      <div className="mt-4 flex items-center justify-end gap-2.5">
        <button
          onClick={onCancel}
          disabled={isConfirming}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 transition-colors"
        >
          <X className="w-3.5 h-3.5" />
          <span>Cancel</span>
        </button>
        <button
          onClick={onConfirm}
          disabled={isConfirming}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-xs font-semibold shadow-sm shadow-brand-500/30 transition-all hover:scale-[1.02]"
        >
          <Check className="w-3.5 h-3.5" />
          <span>{isConfirming ? 'Executing...' : 'Confirm & Proceed'}</span>
        </button>
      </div>
    </div>
  );
}

