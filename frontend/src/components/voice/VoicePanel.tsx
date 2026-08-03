import React from 'react';
import { Mic, MicOff, Square, Sparkles } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';
import { Waveform } from './Waveform';

export const VoicePanel: React.FC = () => {
  const { voiceState, setVoiceState, setActiveView } = useAuraStore();

  const handleToggleState = () => {
    if (voiceState === 'idle') setVoiceState('listening');
    else if (voiceState === 'listening') setVoiceState('thinking');
    else setVoiceState('idle');
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-slate-950/60 select-none">
      <div className="w-full max-w-lg glass-panel border border-slate-800 rounded-3xl p-8 flex flex-col items-center shadow-2xl text-center space-y-6">
        
        {/* Status Badge */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-400">
          <Sparkles className="w-3.5 h-3.5 animate-spin" />
          <span className="capitalize">Status: {voiceState}</span>
        </div>

        {/* Animated Waveform */}
        <Waveform state={voiceState} />

        {/* Status Text */}
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-slate-100">
            {voiceState === 'listening' && 'Listening to your command...'}
            {voiceState === 'thinking' && 'Processing intent & reasoning...'}
            {voiceState === 'speaking' && 'AURA Speaking...'}
            {voiceState === 'idle' && 'Click microphone to speak'}
          </h2>
          <p className="text-xs text-slate-400 font-mono">Whisper STT • Edge TTS • &lt; 45ms Latency</p>

        </div>

        {/* Voice Control Buttons */}
        <div className="flex items-center gap-4 pt-4">
          <button
            onClick={handleToggleState}
            className={`w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-xl ${
              voiceState === 'listening'
                ? 'bg-rose-500 text-white shadow-rose-500/30 animate-pulse'
                : 'bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-cyan-500/30 hover:scale-105'
            }`}
          >
            {voiceState === 'listening' ? <Square className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
          </button>

          <button
            onClick={() => setActiveView('chat')}
            className="px-4 py-2 rounded-xl glass-panel text-xs text-slate-300 hover:text-slate-100 hover:bg-slate-800 transition-all font-mono"
          >
            Switch to Chat
          </button>
        </div>
      </div>
    </div>
  );
};
