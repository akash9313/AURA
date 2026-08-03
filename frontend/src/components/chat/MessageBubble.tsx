import React from 'react';
import { Sparkles, User } from 'lucide-react';
import { Message } from '../../types/aura';
import { CodeBlock } from './CodeBlock';
import { InteractiveCard } from './InteractiveCard';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  // Simple Markdown parsing for code blocks
  const renderFormattedContent = (content: string) => {
    if (content.includes('```')) {
      const parts = content.split(/```/);
      return parts.map((part, index) => {
        if (index % 2 === 1) {
          const lines = part.split('\n');
          const lang = lines[0].trim() || 'bash';
          const code = lines.slice(1).join('\n') || part;
          return <CodeBlock key={index} code={code} language={lang} />;
        }
        return <p key={index} className="whitespace-pre-wrap leading-relaxed">{part}</p>;
      });
    }
    return <p className="whitespace-pre-wrap leading-relaxed">{content}</p>;
  };

  return (
    <div className={`flex gap-3.5 my-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
        isUser
          ? 'bg-slate-800 text-slate-300 border border-slate-700'
          : 'bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-cyan-500/20'
      }`}>
        {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4 animate-pulse" />}
      </div>

      {/* Bubble Content */}
      <div className={`max-w-[75%] space-y-2`}>
        <div className={`px-4 py-3 rounded-2xl text-sm ${
          isUser
            ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white rounded-tr-none shadow-lg shadow-cyan-500/10'
            : 'glass-panel text-slate-200 rounded-tl-none border border-slate-800'
        }`}>
          {renderFormattedContent(message.content)}
        </div>

        {/* Optional Tool Calls */}
        {message.toolCalls && message.toolCalls.map((tc, idx) => (
          <InteractiveCard key={idx} tool={tc.tool} status={tc.status} result={tc.result} />
        ))}

        <span className={`block text-[10px] text-slate-500 font-mono ${isUser ? 'text-right' : 'text-left'}`}>
          {message.timestamp}
        </span>
      </div>
    </div>
  );
};
