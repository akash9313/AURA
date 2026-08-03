import React from 'react';
import { Activity, HardDrive, Wifi } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';

export const StatusBar: React.FC = () => {
  const { activeWorkflow } = useAuraStore();
  const activeTaskCount = activeWorkflow ? activeWorkflow.tasks.filter(t => t.status === 'running' || t.status === 'pending').length : 0;

  return (
    <footer className="h-7 glass-panel border-t border-slate-800/80 px-4 flex items-center justify-between text-[11px] font-mono text-slate-400 select-none z-10">
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-1.5 text-cyan-400">
          <Activity className="w-3 h-3" />
          <span>{activeTaskCount > 0 ? `${activeTaskCount} active task(s)` : 'Engine Idle'}</span>
        </span>
        <span className="text-slate-600">|</span>
        <span className="flex items-center gap-1 text-slate-400">
          <HardDrive className="w-3 h-3 text-slate-500" />
          <span>RAM: 184 MB</span>
        </span>
      </div>

      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1 text-emerald-400">
          <Wifi className="w-3 h-3" />
          <span>Local Core Ready</span>
        </span>
      </div>
    </footer>
  );
};
