import React from 'react';
import { Terminal, Activity, CheckCircle2, Cpu, ShieldCheck } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';

export const DeveloperMode: React.FC = () => {
  const { devLogs } = useAuraStore();

  const services = [
    { name: 'AuraEngine Core', status: 'Running', health: '100%' },
    { name: 'SpeechService', status: 'Running', health: '98%' },
    { name: 'BrainService', status: 'Running', health: '100%' },
    { name: 'MemoryService', status: 'Running', health: '100%' },
    { name: 'VisionService', status: 'Running', health: '99%' },
    { name: 'CognitiveService', status: 'Running', health: '100%' },
    { name: 'AgentService', status: 'Running', health: '100%' },
    { name: 'WindowsService', status: 'Running', health: '100%' },
    { name: 'BrowserService', status: 'Running', health: '97%' },
  ];

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto space-y-6 bg-slate-950/40 font-mono">
      <div>
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Terminal className="w-5 h-5 text-cyan-400" />
          <span>Developer Tools & EventBus Inspector</span>
        </h2>
        <p className="text-xs text-slate-400 font-sans mt-0.5">Real-time Event Streams, Service Health, and Execution Telemetry</p>
      </div>

      {/* Services Health Matrix */}
      <div className="grid grid-cols-3 gap-3">
        {services.map((s, idx) => (
          <div key={idx} className="p-3 glass-panel border border-slate-800 rounded-xl flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-200 font-semibold">{s.name}</span>
            </div>
            <span className="text-cyan-400 font-mono">{s.health}</span>
          </div>
        ))}
      </div>

      {/* Real-time EventBus Logs */}
      <div className="glass-panel border border-slate-800 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <span className="text-xs font-semibold text-slate-300">Live EventBus Telemetry Stream</span>
          <span className="text-[10px] text-cyan-400">{devLogs.length} events logged</span>
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto font-mono text-xs">
          {devLogs.map((log) => (
            <div key={log.id} className="p-2.5 bg-slate-950/80 border border-slate-900 rounded-xl flex items-start gap-3">
              <span className="text-slate-500 text-[10px] whitespace-nowrap">{log.timestamp}</span>
              <span className="px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 font-bold text-[10px]">
                {log.eventType}
              </span>
              <pre className="text-slate-400 text-[11px] flex-1 overflow-x-auto">
                {JSON.stringify(log.payload)}
              </pre>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
