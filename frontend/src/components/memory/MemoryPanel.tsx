import React, { useState } from 'react';
import { Database, Search, Pin, Trash2, Plus, FileText, UserCheck, BookOpen } from 'lucide-react';
import { useAuraStore } from '../../store/useAuraStore';

export const MemoryPanel: React.FC = () => {
  const { memories, toggleMemoryPin, deleteMemory, addMemory } = useAuraStore();
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<string>('all');

  const filtered = memories.filter(m => {
    const matchesType = filterType === 'all' || m.type === filterType;
    const matchesQuery = m.title.toLowerCase().includes(search.toLowerCase()) || m.content.toLowerCase().includes(search.toLowerCase());
    return matchesType && matchesQuery;
  });

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto space-y-6 bg-slate-950/40">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Database className="w-5 h-5 text-cyan-400" />
            <span>Memory Engine Explorer</span>
          </h2>
          <p className="text-xs text-slate-400 font-sans mt-0.5">Inspect & Manage Working, Conversation, Profile, and Knowledge Repositories</p>
        </div>

        <button
          onClick={() => addMemory({ type: 'profile', title: 'New User Preference', content: 'Custom preference entry', pinned: false })}
          className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-indigo-600 text-white px-3.5 py-2 rounded-xl text-xs font-semibold hover:shadow-lg hover:shadow-cyan-500/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Add Memory</span>
        </button>
      </div>

      {/* Filter Tabs & Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search memory facts & context..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900/80 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex bg-slate-900/80 border border-slate-800 p-1 rounded-xl text-xs font-mono">
          {['all', 'working', 'conversation', 'profile', 'knowledge'].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1 rounded-lg capitalize transition-all ${
                filterType === type ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Memory Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((mem) => (
          <div key={mem.id} className="glass-panel border border-slate-800 rounded-2xl p-4 space-y-3 relative group">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                {mem.type === 'profile' && <UserCheck className="w-4 h-4 text-cyan-400" />}
                {mem.type === 'knowledge' && <BookOpen className="w-4 h-4 text-indigo-400" />}
                {mem.type === 'working' && <FileText className="w-4 h-4 text-amber-400" />}
                <h3 className="text-sm font-semibold text-slate-200">{mem.title}</h3>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={() => toggleMemoryPin(mem.id)}
                  className={`p-1 rounded-lg transition-colors ${mem.pinned ? 'text-cyan-400' : 'text-slate-600 hover:text-slate-300'}`}
                >
                  <Pin className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => deleteMemory(mem.id)}
                  className="p-1 text-slate-600 hover:text-rose-400 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <p className="text-xs text-slate-300 font-mono leading-relaxed bg-slate-950/60 p-2.5 rounded-xl border border-slate-900">
              {mem.content}
            </p>

            <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span className="uppercase tracking-wider font-semibold text-cyan-400">{mem.type}</span>
              <span>{mem.timestamp}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
