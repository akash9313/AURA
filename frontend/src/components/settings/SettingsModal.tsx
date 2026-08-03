import React from 'react';
import { Settings, Cpu, Mic, Shield, Moon, Bell } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';

export const SettingsModal: React.FC = () => {
  const { settings, updateSettings } = useAuraStore();

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto space-y-6 bg-slate-950/40 font-sans">
      <div>
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Settings className="w-5 h-5 text-cyan-400" />
          <span>System Settings</span>
        </h2>
        <p className="text-xs text-slate-400 font-sans mt-0.5">Configure AI Providers, Speech Engine, Privacy, and Execution Policies</p>
      </div>

      <div className="max-w-2xl space-y-6">
        {/* AI Provider Section */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>AI Reasoning Provider</span>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'gemini', name: 'Google Gemini Pro' },
              { id: 'openai', name: 'OpenAI GPT-4o' },
              { id: 'local', name: 'Local Ollama Llama3' },
            ].map((p) => (
              <button
                key={p.id}
                onClick={() => updateSettings({ aiProvider: p.id as any })}
                className={`p-3 rounded-xl border text-xs font-mono font-medium transition-all ${
                  settings.aiProvider === p.id
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-md shadow-cyan-500/10'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        {/* Speech Provider */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Mic className="w-4 h-4 text-indigo-400" />
            <span>Speech & Voice Engine</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {[
              { id: 'edge-tts', name: 'Microsoft Edge TTS (Neural)' },
              { id: 'system', name: 'Local SAPI5 System Voice' },
            ].map((s) => (
              <button
                key={s.id}
                onClick={() => updateSettings({ voiceProvider: s.id as any })}
                className={`p-3 rounded-xl border text-xs font-mono font-medium transition-all ${
                  settings.voiceProvider === s.id
                    ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40 shadow-md shadow-indigo-500/10'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {s.name}
              </button>
            ))}
          </div>
        </div>

        {/* Privacy & Safety Toggles */}
        <div className="glass-panel border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span>Privacy & Action Safety Policies</span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <label className="flex items-center justify-between p-3 bg-slate-900/60 border border-slate-800 rounded-xl cursor-pointer">
              <span className="text-slate-300">Require Confirmation for Sensitive Tools</span>
              <input
                type="checkbox"
                checked={settings.requireConfirmation}
                onChange={(e) => updateSettings({ requireConfirmation: e.target.checked })}
                className="w-4 h-4 accent-cyan-500 rounded"
              />
            </label>

            <label className="flex items-center justify-between p-3 bg-slate-900/60 border border-slate-800 rounded-xl cursor-pointer">
              <span className="text-slate-300">Privacy Mode (Disable External Analytics)</span>
              <input
                type="checkbox"
                checked={settings.privacyMode}
                onChange={(e) => updateSettings({ privacyMode: e.target.checked })}
                className="w-4 h-4 accent-cyan-500 rounded"
              />
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};
