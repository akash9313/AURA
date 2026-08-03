import React from 'react';
import { Search, Command, Cpu, ShieldCheck } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';

export const Header: React.FC = () => {
  const { setCommandPaletteOpen, settings } = useAuraStore();

  return (
    <header className="h-14 glass-panel border-b border-slate-800/80 px-6 flex items-center justify-between select-none z-10">
      {/* Search & Command Palette Trigger */}
      <button
        onClick={() => setCommandPaletteOpen(true)}
        className="flex items-center gap-3 bg-slate-900/60 hover:bg-slate-800/60 border border-slate-800 text-slate-400 hover:text-slate-200 px-3.5 py-1.5 rounded-xl text-xs transition-all w-72"
      >
        <Search className="w-3.5 h-3.5 text-slate-400" />
        <span className="flex-1 text-left">Search commands, tools, memory...</span>
        <kbd className="flex items-center gap-0.5 bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px] text-slate-300 font-mono">
          <Command className="w-2.5 h-2.5" /> K
        </kbd>
      </button>

      {/* System Indicators */}
      <div className="flex items-center gap-4 text-xs font-mono">
        <div className="flex items-center gap-2 bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 px-2.5 py-1 rounded-lg">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span className="capitalize">{settings.aiProvider} LLM</span>
        </div>

        <div className="flex items-center gap-1.5 text-emerald-400 bg-emerald-950/30 border border-emerald-500/20 px-2.5 py-1 rounded-lg">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Core Online</span>
        </div>
      </div>
    </header>
  );
};
