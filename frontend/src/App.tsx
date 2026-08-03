import React from 'react';
import { useAuraStore } from './store/useAuraStore';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { StatusBar } from './components/layout/StatusBar';
import { CommandPalette } from './components/layout/CommandPalette';

import { ConversationArea } from './components/chat/ConversationArea';
import { VoicePanel } from './components/voice/VoicePanel';
import { ToolActivityPanel } from './components/activity/ToolActivityPanel';
import { MemoryPanel } from './components/memory/MemoryPanel';
import { PluginStore } from './components/plugins/PluginStore';
import { DeveloperMode } from './components/devmode/DeveloperMode';
import { SettingsModal } from './components/settings/SettingsModal';

export const App: React.FC = () => {
  const { activeView } = useAuraStore();

  return (
    <div className="flex h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden font-sans select-none">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Container */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header Bar */}
        <Header />

        {/* Dynamic View Panel */}
        <main className="flex-1 overflow-hidden flex flex-col relative">
          {activeView === 'chat' && <ConversationArea />}
          {activeView === 'voice' && <VoicePanel />}
          {activeView === 'activity' && <ToolActivityPanel />}
          {activeView === 'memory' && <MemoryPanel />}
          {activeView === 'plugins' && <PluginStore />}
          {activeView === 'devmode' && <DeveloperMode />}
          {activeView === 'settings' && <SettingsModal />}
        </main>

        {/* Footer Status Bar */}
        <StatusBar />
      </div>

      {/* Global Command Palette (Ctrl+K) */}
      <CommandPalette />
    </div>
  );
};
