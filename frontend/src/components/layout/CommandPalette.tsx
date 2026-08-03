import React, { useState, useEffect } from 'react';
import { Search, Terminal, MessageSquare, Database, Settings, Sparkles, X } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';

export const CommandPalette: React.FC = () => {
  const { isCommandPaletteOpen, setCommandPaletteOpen, setActiveView } = useAuraStore();
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(!isCommandPaletteOpen);
      } else if (e.key === 'Escape' && isCommandPaletteOpen) {
        setCommandPaletteOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandPaletteOpen, setCommandPaletteOpen]);

  if (!isCommandPaletteOpen) return null;

  const commands = [
    { label: 'Open Chat View', view: 'chat', icon: MessageSquare },
    { label: 'Open Voice Mode', view: 'voice', icon: Sparkles },
    { label: 'Inspect Task Activity', view: 'activity', icon: Terminal },
    { label: 'Browse Memory Explorer', view: 'memory', icon: Database },
    { label: 'Open System Settings', view: 'settings', icon: Settings },
  ];

  const filtered = commands.filter(c => c.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-start justify-center pt-24 z-50 animate-in fade-in duration-150">
      <div className="w-[540px] glass-panel border border-slate-700/60 rounded-2xl shadow-2xl overflow-hidden">
        {/* Input Header */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-slate-800">
          <Search className="w-4 h-4 text-cyan-400" />
          <input
            type="text"
            autoFocus
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent border-none text-slate-100 text-sm focus:outline-none placeholder-slate-500 font-sans"
          />
          <button
            onClick={() => setCommandPaletteOpen(false)}
            className="text-slate-500 hover:text-slate-300 p-1 rounded-lg"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Command Options List */}
        <div className="p-2 space-y-1 max-h-80 overflow-y-auto">
          {filtered.map((cmd, idx) => {
            const Icon = cmd.icon;
            return (
              <button
                key={idx}
                onClick={() => {
                  setActiveView(cmd.view as any);
                  setCommandPaletteOpen(false);
                }}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium text-slate-300 hover:text-cyan-300 hover:bg-slate-800/80 transition-all text-left group"
              >
                <Icon className="w-4 h-4 text-slate-400 group-hover:text-cyan-400" />
                <span className="flex-1">{cmd.label}</span>
                <span className="text-[10px] text-slate-500 font-mono">Execute</span>
              </button>
            );
          })}
          {filtered.length === 0 && (
            <div className="py-8 text-center text-xs text-slate-500 font-mono">
              No matching commands found
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
