import React from 'react';
import { Grid, Star, Download, CheckCircle, Shield } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';

export const PluginStore: React.FC = () => {
  const { plugins, togglePluginInstall } = useAuraStore();

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto space-y-6 bg-slate-950/40">
      <div>
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Grid className="w-5 h-5 text-cyan-400" />
          <span>AURA Ecosystem Plugin Marketplace</span>
        </h2>
        <p className="text-xs text-slate-400 font-sans mt-0.5">Extend AURA capabilities with verified sandboxed plugins</p>
      </div>

      {/* Grid of Plugins */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {plugins.map((plugin) => (
          <div key={plugin.id} className="glass-panel border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800 text-cyan-400 uppercase">
                  {plugin.category}
                </span>
                <div className="flex items-center gap-1 text-amber-400 text-xs font-mono">
                  <Star className="w-3.5 h-3.5 fill-amber-400" />
                  <span>{plugin.rating.toFixed(1)}</span>
                </div>
              </div>

              <h3 className="text-sm font-bold text-slate-100">{plugin.name}</h3>
              <p className="text-xs text-slate-400 font-sans leading-relaxed">{plugin.description}</p>
            </div>

            <div className="space-y-3 pt-3 border-t border-slate-800/80">
              <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                <span>By {plugin.author}</span>
                <span>v{plugin.version}</span>
              </div>

              <button
                onClick={() => togglePluginInstall(plugin.id)}
                className={`w-full py-2 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                  plugin.installed
                    ? 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-rose-400 hover:border-rose-500/30'
                    : 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-500/10'
                }`}
              >
                {plugin.installed ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span>Installed (Click to Remove)</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Install Plugin</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
