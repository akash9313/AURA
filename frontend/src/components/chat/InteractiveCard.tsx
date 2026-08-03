import React from 'react';
import { Terminal, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface InteractiveCardProps {
  tool: string;
  status: 'running' | 'completed' | 'failed';
  result?: string;
}

export const InteractiveCard: React.FC<InteractiveCardProps> = ({ tool, status, result }) => {
  return (
    <div className="my-2 p-3 glass-panel border border-slate-800 rounded-xl flex items-center justify-between text-xs font-mono">
      <div className="flex items-center gap-3">
        <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-cyan-400">
          <Terminal className="w-4 h-4" />
        </div>
        <div>
          <span className="font-semibold text-slate-200">{tool}</span>
          {result && <p className="text-[11px] text-slate-400 font-sans mt-0.5">{result}</p>}
        </div>
      </div>

      <div className="flex items-center gap-1.5">
        {status === 'completed' && (
          <span className="flex items-center gap-1 text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded-md text-[10px]">
            <CheckCircle className="w-3 h-3" />
            <span>Success</span>
          </span>
        )}
        {status === 'running' && (
          <span className="flex items-center gap-1 text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded-md text-[10px] animate-pulse">
            <Clock className="w-3 h-3" />
            <span>Executing...</span>
          </span>
        )}
        {status === 'failed' && (
          <span className="flex items-center gap-1 text-rose-400 bg-rose-950/40 px-2 py-0.5 rounded-md text-[10px]">
            <AlertCircle className="w-3 h-3" />
            <span>Failed</span>
          </span>
        )}
      </div>
    </div>
  );
};
