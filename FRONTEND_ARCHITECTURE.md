# AURA Desktop — Frontend Architecture & UI Specification

> **Document Status**: Approved Architecture Specification  
> **Target Platform**: Desktop (Windows, macOS, Linux) via Tauri 2.0 + React 18 + TypeScript + Vite + TailwindCSS + Framer Motion  

---

## 1. Architectural Overview

AURA Desktop is designed as a **Cognitive AI Operating System Shell**, offering a dark-first, glassmorphism-enhanced desktop interface that communicates asynchronously with the local Python `AuraEngine` core.

### 1.1 Stack Selection: Tauri 2.0 vs Electron
After architectural evaluation, **Tauri 2.0 + React + TypeScript + Vite** was chosen over Electron:

| Metric | Tauri 2.0 + React | Electron + React |
| :--- | :--- | :--- |
| **Binary Bundle Size** | ~15 – 20 MB | ~150 – 200 MB |
| **Idle Memory Footprint** | < 250 MB RAM | > 850 MB RAM |
| **Startup Latency** | < 1.2 seconds | > 3.8 seconds |
| **Security Architecture** | OS Sandboxed Webview + Rust IPC | Node.js Runtime Integration |
| **Webview Engine** | Native OS (WebView2 / WebKit) | Bundled Chromium |

---

## 2. Component Hierarchy

```
App Shell (src/App.tsx)
├── Sidebar Navigation (src/components/layout/Sidebar.tsx)
├── Header Bar (src/components/layout/Header.tsx)
├── Dynamic View Area
│   ├── ConversationArea (src/components/chat/ConversationArea.tsx)
│   │   ├── MessageBubble (src/components/chat/MessageBubble.tsx)
│   │   ├── CodeBlock (src/components/chat/CodeBlock.tsx)
│   │   └── InteractiveCard (src/components/chat/InteractiveCard.tsx)
│   ├── VoicePanel (src/components/voice/VoicePanel.tsx)
│   │   └── Waveform Visualizer (src/components/voice/Waveform.tsx)
│   ├── ToolActivityPanel (src/components/activity/ToolActivityPanel.tsx)
│   ├── MemoryPanel (src/components/memory/MemoryPanel.tsx)
│   ├── PluginStore (src/components/plugins/PluginStore.tsx)
│   ├── DeveloperMode (src/components/devmode/DeveloperMode.tsx)
│   └── SettingsModal (src/components/settings/SettingsModal.tsx)
├── StatusBar Footer (src/components/layout/StatusBar.tsx)
└── CommandPalette Modal (src/components/layout/CommandPalette.tsx) [Ctrl+K]
```

---

## 3. State Management (Zustand)

State is centrally managed via `useAuraStore` (`src/store/useAuraStore.ts`):

- `activeView`: Active primary view (`chat` | `voice` | `activity` | `memory` | `plugins` | `devmode` | `settings`).
- `voiceState`: Current voice state (`idle` | `listening` | `thinking` | `speaking`).
- `isCommandPaletteOpen`: Boolean modal toggle for global search (`Ctrl+K`).
- `messages`: Active conversation stream buffer.
- `activeWorkflow`: Real-time task graph execution state.
- `memories`: Working, Conversation, Profile, and Knowledge items.
- `plugins`: Marketplace installed and available plugin items.
- `devLogs`: Real-time telemetry log events from backend `EventBus`.
- `settings`: AI Provider, Speech Provider, Theme, and Privacy configuration.

---

## 4. Directory Structure

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── styles/
    │   └── globals.css
    ├── types/
    │   └── aura.ts
    ├── store/
    │   └── useAuraStore.ts
    ├── services/
    │   └── api.ts
    └── components/
        ├── layout/
        │   ├── Sidebar.tsx
        │   ├── Header.tsx
        │   ├── StatusBar.tsx
        │   └── CommandPalette.tsx
        ├── chat/
        │   ├── ConversationArea.tsx
        │   ├── MessageBubble.tsx
        │   ├── CodeBlock.tsx
        │   └── InteractiveCard.tsx
        ├── voice/
        │   ├── VoicePanel.tsx
        │   └── Waveform.tsx
        ├── activity/
        │   └── ToolActivityPanel.tsx
        ├── memory/
        │   └── MemoryPanel.tsx
        ├── plugins/
        │   └── PluginStore.tsx
        ├── devmode/
        │   └── DeveloperMode.tsx
        └── settings/
            └── SettingsModal.tsx
```

---

## 5. Design Tokens & Glassmorphism System

### 5.1 CSS Tokens (`globals.css`)
- **Background**: `hsl(224 71% 4%)` (`#030712`)
- **Card**: `hsl(224 71% 6%)` (`#090d16`)
- **Primary**: `hsl(199 89% 48%)` (Cyan Accent `#0ea5e9`)
- **Accent**: `hsl(263 70% 50%)` (Indigo Accent `#6366f1`)
- **Glass Panel**: `background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(16px);`

---

## 6. Backend Integration Bridge

The frontend communicates with the local Python backend via `AuraAPIService` (`src/services/api.ts`). In production, this connects via WebSocket / IPC to listen for backend `EventBus` signals (`GOAL_CREATED`, `WORKFLOW_COMPLETED`, `AI_RESPONSE_READY`) and update the Zustand state store in real-time.
