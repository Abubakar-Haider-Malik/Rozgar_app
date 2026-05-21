'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ChatUI({ 
  onSend, 
  isLoading, 
  demos 
}: { 
  onSend: (text: string) => void;
  isLoading: boolean;
  demos: any[];
}) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 p-4 overflow-y-auto space-y-6">
        <div className="text-center mb-8">
          <div className="bg-brand-500/20 text-brand-400 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border border-brand-500/50">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold mb-2">KaamKar AI</h1>
          <p className="text-gray-400">Your smart orchestration assistant for informal services.</p>
        </div>

        {demos.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8">
            {demos.map((demo) => (
              <button
                key={demo.id}
                onClick={() => onSend(demo.text)}
                disabled={isLoading}
                className="text-left p-3 rounded-xl glass-panel hover:bg-surface-700 transition-colors disabled:opacity-50"
              >
                <div className="font-semibold text-brand-400 mb-1">{demo.title}</div>
                <div className="text-sm text-gray-400">"{demo.text}"</div>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="p-4 border-t border-surface-700 bg-surface-800/80 backdrop-blur">
        <div className="flex items-end gap-2 max-w-4xl mx-auto">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Mujhe kal subah G-13 mein plumber chahiye..."
            className="w-full bg-surface-900 border border-surface-600 rounded-2xl px-4 py-3 text-white focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-brand-600 hover:bg-brand-500 disabled:bg-surface-700 disabled:text-gray-500 text-white rounded-2xl p-4 transition-colors flex-shrink-0"
          >
            {isLoading ? (
              <div className="flex gap-1 items-center justify-center h-6 w-6">
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" />
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
