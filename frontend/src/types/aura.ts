export type ViewMode = 'chat' | 'voice' | 'activity' | 'memory' | 'plugins' | 'devmode' | 'settings';

export type VoiceState = 'idle' | 'listening' | 'thinking' | 'speaking';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  toolCalls?: Array<{
    tool: string;
    result?: string;
    status: 'running' | 'completed' | 'failed';
  }>;
}

export interface TaskItem {
  id: string;
  tool: string;
  parameters: Record<string, any>;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration?: number;
}

export interface WorkflowState {
  workflowId: string;
  goal: string;
  status: 'created' | 'running' | 'completed' | 'failed';
  tasks: TaskItem[];
}

export interface MemoryItem {
  id: string;
  type: 'working' | 'conversation' | 'profile' | 'knowledge';
  title: string;
  content: string;
  pinned: boolean;
  timestamp: string;
}

export interface PluginItem {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  installed: boolean;
  category: 'windows' | 'browser' | 'vision' | 'productivity' | 'developer';
  rating: number;
}

export interface DevLogEvent {
  id: string;
  timestamp: string;
  eventType: string;
  payload: any;
}

export interface SystemSettings {
  aiProvider: 'gemini' | 'openai' | 'local';
  voiceProvider: 'edge-tts' | 'system';
  theme: 'dark' | 'glass' | 'cyber' | 'minimal';
  autoSpeak: boolean;
  privacyMode: boolean;
  requireConfirmation: boolean;
}
