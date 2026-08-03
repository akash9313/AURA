import React from 'react';
import { Activity, CheckCircle2, Clock, AlertTriangle, Terminal, Play } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';

export const ToolActivityPanel: React.FC = () => {
  const { activeWorkflow } = useAuraStore();

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto space-y-6 bg-slate-950/40 font-mono">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span>Task & Tool Activity Panel</span>
          </h2>
          <p className="text-xs text-slate-400 font-sans mt-0.5">Real-time Task Graph Execution Engine Monitoring</p>
        </div>
      </div>

      {/* Active Workflow Card */}
      {activeWorkflow ? (
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider">Active Goal</span>
              <h3 className="text-sm font-semibold text-cyan-300 font-sans mt-0.5">{activeWorkflow.goal}</h3>
            </div>
            <span className="px-2.5 py-1 rounded-full text-xs font-mono bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 capitalize">
              {activeWorkflow.status}
            </span>
          </div>

          {/* Execution Timeline */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Execution Timeline</h4>
            <div className="space-y-2">
              {activeWorkflow.tasks.map((task) => (
                <div key={task.id} className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center justify-between text-xs">
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 rounded-lg bg-slate-800 text-cyan-400">
                      <Terminal className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-slate-200 font-bold">{task.tool}</span>
                      <p className="text-[11px] text-slate-500 font-sans mt-0.5">Params: {JSON.stringify(task.parameters)}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {task.duration && <span className="text-[11px] text-slate-500">{task.duration}s</span>}
                    {task.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {task.status === 'running' && <Clock className="w-4 h-4 text-cyan-400 animate-spin" />}
                    {task.status === 'failed' && <AlertTriangle className="w-4 h-4 text-rose-400" />}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-panel border border-slate-800 rounded-2xl p-12 text-center text-slate-500 text-xs">
          No active workflow running.
        </div>
      )}
    </div>
  );
};
