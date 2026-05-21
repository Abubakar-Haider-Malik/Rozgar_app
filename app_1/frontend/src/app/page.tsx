'use client';

import { useState, useEffect } from 'react';
import ChatUI from '@/components/ChatUI';
import AgentTrace from '@/components/AgentTrace';
import { submitServiceRequest, fetchDemos } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';

export default function Home() {
  const [demos, setDemos] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDemos().then(setDemos).catch(console.error);
  }, []);

  const handleSend = async (text: string) => {
    setIsLoading(true);
    setResult(null);
    setError(null);
    
    try {
      const data = await submitServiceRequest(text);
      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Pipeline failed');
        setResult(data); // Show trace even on failure
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="h-screen flex bg-surface-900 overflow-hidden">
      {/* Left Pane - Chat & Results */}
      <div className="flex-1 flex flex-col relative border-r border-surface-700">
        {!result && !isLoading && (
          <div className="flex-1 overflow-hidden">
            <ChatUI onSend={handleSend} isLoading={isLoading} demos={demos} />
          </div>
        )}

        {isLoading && (
          <div className="flex-1 flex items-center justify-center p-8 flex-col gap-4">
            <div className="w-16 h-16 border-4 border-brand-500/20 border-t-brand-500 rounded-full animate-spin" />
            <h3 className="text-xl font-medium animate-pulse">Orchestrating agents...</h3>
            <p className="text-gray-400">Please wait while our AI system processes your request.</p>
          </div>
        )}

        {result && (
          <div className="flex-1 overflow-y-auto p-4 md:p-8">
            <button 
              onClick={() => { setResult(null); setError(null); }}
              className="mb-6 flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
              New Request
            </button>

            {error && (
              <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl mb-6">
                <strong>Error:</strong> {error}
              </div>
            )}

            {result.success && result.booking && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-panel p-6 rounded-2xl mb-6 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-4">
                  <span className="bg-brand-500/20 text-brand-400 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border border-brand-500/30">
                    {result.booking.status}
                  </span>
                </div>
                
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                  <span className="bg-brand-500 text-white p-2 rounded-lg">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                  </span>
                  Booking Confirmed!
                </h2>

                <div className="grid grid-cols-2 gap-4 mb-6 bg-surface-800 rounded-xl p-4">
                  <div>
                    <span className="block text-sm text-gray-400 mb-1">Provider</span>
                    <span className="font-medium text-lg">{result.booking.provider.name}</span>
                  </div>
                  <div>
                    <span className="block text-sm text-gray-400 mb-1">Service</span>
                    <span className="font-medium text-lg">{result.booking.service}</span>
                  </div>
                  <div>
                    <span className="block text-sm text-gray-400 mb-1">Location</span>
                    <span className="font-medium">{result.booking.location}</span>
                  </div>
                  <div>
                    <span className="block text-sm text-gray-400 mb-1">Time Slot</span>
                    <span className="font-medium">{result.booking.slot}</span>
                  </div>
                </div>

                <div className="flex justify-between items-center bg-surface-900 rounded-xl p-4 border border-surface-700">
                  <div>
                    <span className="block text-sm text-gray-400">Estimated Cost</span>
                    <span className="font-bold text-brand-400">{result.booking.estimated_cost}</span>
                  </div>
                  <div className="text-right">
                    <span className="block text-sm text-gray-400">Provider ETA</span>
                    <span className="font-bold">{result.booking.eta_minutes} mins</span>
                  </div>
                </div>
              </motion.div>
            )}
            
            {result.notifications?.confirmation && (
               <motion.div 
                 initial={{ opacity: 0, y: 20 }}
                 animate={{ opacity: 1, y: 0 }}
                 transition={{ delay: 0.2 }}
                 className="bg-[#0b141a] text-[#e9edef] rounded-xl overflow-hidden max-w-sm ml-auto border border-surface-700"
               >
                 <div className="bg-[#202c33] p-3 flex items-center gap-3">
                    <div className="w-8 h-8 bg-brand-600 rounded-full flex items-center justify-center">KA</div>
                    <span className="font-medium">KaamKar AI</span>
                 </div>
                 <div className="p-4 bg-[#0b141a] bg-[url('https://static.whatsapp.net/rsrc.php/v3/yl/r/11MPEo3J08E.png')] bg-repeat">
                    <div className="bg-[#005c4b] p-3 rounded-lg rounded-tr-none inline-block whitespace-pre-wrap float-right shadow-sm">
                      {result.notifications.confirmation}
                    </div>
                    <div className="clear-both"></div>
                 </div>
               </motion.div>
            )}

          </div>
        )}
      </div>

      {/* Right Pane - Agent Traces */}
      <div className="hidden lg:block w-1/3 p-4">
        <AgentTrace logs={result?.trace_log || []} />
      </div>
    </main>
  );
}
