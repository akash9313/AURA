import { create } from 'zustand';
import { DevLogEvent, MemoryItem, Message, PluginItem, SystemSettings, TaskItem, ViewMode, VoiceState, WorkflowState } from '../types/aura';

interface AuraStoreState {
  activeView: ViewMode;
  voiceState: VoiceState;
  isCommandPaletteOpen: boolean;
  messages: Message[];
  activeWorkflow: WorkflowState | null;
  memories: MemoryItem[];
  plugins: PluginItem[];
  devLogs: DevLogEvent[];
  settings: SystemSettings;

  // Actions
  setActiveView: (view: ViewMode) => void;
  setVoiceState: (state: VoiceState) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  addMessage: (msg: Omit<Message, 'id' | 'timestamp'>) => void;
  setWorkflow: (workflow: WorkflowState | null) => void;
  addMemory: (memory: Omit<MemoryItem, 'id' | 'timestamp'>) => void;
  toggleMemoryPin: (id: string) => void;
  deleteMemory: (id: string) => void;
  togglePluginInstall: (id: string) => void;
  addDevLog: (eventType: string, payload: any) => void;
  updateSettings: (newSettings: Partial<SystemSettings>) => void;
}

export const useAuraStore = create<AuraStoreState>((set) => ({
  activeView: 'chat',
  voiceState: 'idle',
  isCommandPaletteOpen: false,
  messages: [
    {
      id: 'm1',
      role: 'assistant',
      content: 'Welcome to **AURA AI Operating System**.\nHow can I assist your workflow today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ],
  activeWorkflow: {
    workflowId: 'wf_demo_1',
    goal: 'AURA Desktop Initialized',
    status: 'completed',
    tasks: [
      { id: 't1', tool: 'open_application', parameters: { application: 'AURA Engine' }, status: 'completed', duration: 0.12 },
      { id: 't2', tool: 'read_screen', parameters: {}, status: 'completed', duration: 0.25 }
    ]
  },
  memories: [
    { id: 'mem_1', type: 'profile', title: 'User Identity', content: 'Primary Operator: Akash', pinned: true, timestamp: '10:00 AM' },
    { id: 'mem_2', type: 'knowledge', title: 'AURA Architecture', content: 'AuraEngine core event-driven kernel with cognitive loop.', pinned: false, timestamp: '10:15 AM' }
  ],
  plugins: [
    { id: 'p1', name: 'Windows Controller', description: 'Native Windows app control & window management', author: 'AURA Core Team', version: '1.0.0', installed: true, category: 'windows', rating: 5.0 },
    { id: 'p2', name: 'Browser Agent', description: 'Autonomous Playwright web perception & extraction', author: 'AURA Core Team', version: '1.0.0', installed: true, category: 'browser', rating: 4.9 },
    { id: 'p3', name: 'Vision Engine', description: 'Real-time screen OCR & UI element detector', author: 'AURA Core Team', version: '1.0.0', installed: true, category: 'vision', rating: 4.8 }
  ],
  devLogs: [
    { id: 'd1', timestamp: new Date().toLocaleTimeString(), eventType: 'SYSTEM_BOOT', payload: { engine: 'AuraEngine', status: 'RUNNING' } },
    { id: 'd2', timestamp: new Date().toLocaleTimeString(), eventType: 'EVENT_BUS_INIT', payload: { channels: ['TEXT_READY', 'INTENT_READY', 'ACTION_READY'] } }
  ],
  settings: {
    aiProvider: 'gemini',
    voiceProvider: 'edge-tts',
    theme: 'glass',
    autoSpeak: false,
    privacyMode: false,
    requireConfirmation: true
  },

  setActiveView: (view) => set({ activeView: view }),
  setVoiceState: (voiceState) => set({ voiceState }),
  setCommandPaletteOpen: (open) => set({ isCommandPaletteOpen: open }),
  
  addMessage: (msg) => set((state) => ({
    messages: [
      ...state.messages,
      {
        ...msg,
        id: `msg_${Date.now()}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]
  })),

  setWorkflow: (workflow) => set({ activeWorkflow: workflow }),

  addMemory: (mem) => set((state) => ({
    memories: [
      {
        ...mem,
        id: `mem_${Date.now()}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      },
      ...state.memories
    ]
  })),

  toggleMemoryPin: (id) => set((state) => ({
    memories: state.memories.map((m) => m.id === id ? { ...m, pinned: !m.pinned } : m)
  })),

  deleteMemory: (id) => set((state) => ({
    memories: state.memories.filter((m) => m.id !== id)
  })),

  togglePluginInstall: (id) => set((state) => ({
    plugins: state.plugins.map((p) => p.id === id ? { ...p, installed: !p.installed } : p)
  })),

  addDevLog: (eventType, payload) => set((state) => ({
    devLogs: [
      {
        id: `log_${Date.now()}`,
        timestamp: new Date().toLocaleTimeString(),
        eventType,
        payload
      },
      ...state.devLogs.slice(0, 99)
    ]
  })),

  updateSettings: (newSettings) => set((state) => ({
    settings: { ...state.settings, ...newSettings }
  }))
}));
