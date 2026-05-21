'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface TraceLog {
  timestamp: string;
  agent: string;
  action: string;
  tool: string;
  reasoning: string;
  output: any;
}

export default function AgentTrace({ logs }: { logs: TraceLog[] }) {
  if (!logs || logs.length === 0) return null;

  return (
    <div className="w-full glass-panel rounded-2xl p-4 md:p-6 text-sm text-gray-300 h-full overflow-y-auto scrollbar-hide">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="bg-brand-500 w-3 h-3 rounded-full animate-pulse-glow" />
        Agent Reasoning Trace
      </h2>
      
      <div className="space-y-4">
        {logs.map((log, index) => (
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            key={index} 
            className="border-l-2 border-brand-500/50 pl-4 py-1"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-brand-400">{log.agent}</span>
              <span className="text-xs text-gray-500">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <p className="text-white mb-2">{log.action}</p>
            
            <div className="bg-surface-900 rounded p-3 mb-2 border border-surface-700">
              <span className="text-xs uppercase text-gray-500 tracking-wider mb-1 block">Reasoning</span>
              <p className="text-gray-300 leading-relaxed">{log.reasoning}</p>
            </div>
            
            <div className="bg-black/50 rounded p-3 font-mono text-xs overflow-x-auto text-accent-400">
              {JSON.stringify(log.output, null, 2)}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
