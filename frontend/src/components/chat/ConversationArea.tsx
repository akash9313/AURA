import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Sparkles } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';
import { auraAPI } from '../../services/api';
import { MessageBubble } from './MessageBubble';

export const ConversationArea: React.FC = () => {
  const { messages, setActiveView, setVoiceState } = useAuraStore();
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const prompt = input.trim();
    setInput('');
    auraAPI.sendMessage(prompt);
  };

  const handleVoiceTrigger = () => {
    setVoiceState('listening');
    setActiveView('voice');
  };

  return (
    <div className="flex-1 flex flex-col justify-between h-full overflow-hidden bg-slate-950/40">
      {/* Messages List Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input Prompt Form */}
      <div className="p-4 glass-panel border-t border-slate-800/80">
        <form onSubmit={handleSubmit} className="relative flex items-center gap-2 max-w-4xl mx-auto">
          <input
            type="text"
            placeholder="Ask AURA or command your system (e.g. 'Open Notepad', 'Check the screenshot')..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-700/60 hover:border-slate-600 focus:border-cyan-500 text-slate-100 placeholder-slate-500 rounded-2xl px-5 py-3.5 pr-24 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all font-sans shadow-lg"
          />

          <div className="absolute right-3 flex items-center gap-1.5">
            <button
              type="button"
              onClick={handleVoiceTrigger}
              className="p-2 rounded-xl text-slate-400 hover:text-cyan-400 hover:bg-slate-800/60 transition-all"
              title="Voice Mode"
            >
              <Mic className="w-4 h-4" />
            </button>

            <button
              type="submit"
              disabled={!input.trim()}
              className="p-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-cyan-500/25 transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
