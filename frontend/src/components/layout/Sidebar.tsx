import React from 'react';
import { MessageSquare, Mic, Activity, Database, Grid, Terminal, Settings, Sparkles } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';
import { ViewMode } from '../../types/aura';

export const Sidebar: React.FC = () => {
  const { activeView, setActiveView } = useAuraStore();

  const navItems: { id: ViewMode; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'voice', label: 'Voice Mode', icon: Mic },
    { id: 'activity', label: 'Task Activity', icon: Activity },
    { id: 'memory', label: 'Memory Explorer', icon: Database },
    { id: 'plugins', label: 'Plugin Store', icon: Grid },
    { id: 'devmode', label: 'Developer Mode', icon: Terminal },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800 flex flex-col justify-between p-4 select-none z-20">
      <div className="space-y-6">
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Sparkles className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 tracking-wider text-base">AURA AI OS</h1>
            <p className="text-xs text-cyan-400 font-mono">v1.0 • Autonomous Kernel</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/10 text-cyan-300 border border-cyan-500/30 shadow-md shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Settings Bottom Option */}
      <div className="pt-4 border-t border-slate-800/80">
        <button
          onClick={() => setActiveView('settings')}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
            activeView === 'settings'
              ? 'bg-slate-800 text-cyan-300 border border-cyan-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <Settings className="w-4 h-4 text-slate-400" />
          <span>System Settings</span>
        </button>
      </div>
    </aside>
  );
};
