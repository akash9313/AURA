import React from 'react';

interface WaveformProps {
  state: 'idle' | 'listening' | 'thinking' | 'speaking';
}

export const Waveform: React.FC<WaveformProps> = ({ state }) => {
  const bars = [40, 70, 30, 90, 50, 80, 45, 95, 60, 35, 75, 50];

  return (
    <div className="flex items-center justify-center gap-1.5 h-24 my-6">
      {bars.map((height, i) => (
        <div
          key={i}
          className={`w-1.5 rounded-full transition-all duration-300 ${
            state === 'listening'
              ? 'bg-cyan-400 animate-pulse'
              : state === 'thinking'
              ? 'bg-indigo-500 animate-bounce'
              : state === 'speaking'
              ? 'bg-purple-400 animate-pulse'
              : 'bg-slate-700'
          }`}
          style={{
            height: state === 'idle' ? '12px' : `${height}%`,
            animationDelay: `${i * 0.08}s`
          }}
        />
      ))}
    </div>
  );
};
