import { useAuraStore } from '../store/useAuraStore';

export class AuraAPIService {
  private static instance: AuraAPIService;

  public static getInstance(): AuraAPIService {
    if (!AuraAPIService.instance) {
      AuraAPIService.instance = new AuraAPIService();
    }
    return AuraAPIService.instance;
  }

  public async sendMessage(prompt: string): Promise<void> {

    const store = useAuraStore.getState();
    store.addMessage({ role: 'user', content: prompt });
    store.addDevLog('GOAL_CREATED', { goal: prompt });

    // Simulate real-time Cognitive Engine response
    setTimeout(() => {
      let responseText = "I have analyzed your request.";
      const lower = String(prompt).toLowerCase();



      if (lower.includes("notepad") || lower.includes("open")) {
        responseText = "⚡ Application **Notepad** opened successfully via Windows Automation Engine.";
        store.setWorkflow({
          workflowId: `wf_${Date.now()}`,
          goal: prompt,
          status: 'completed',
          tasks: [
            { id: 't1', tool: 'open_application', parameters: { application: 'notepad' }, status: 'completed', duration: 0.15 }
          ]
        });
      } else if (lower.includes("screenshot") || lower.includes("screen")) {
        responseText = "📸 Desktop screen captured and analyzed via Vision Engine.";
        store.setWorkflow({
          workflowId: `wf_${Date.now()}`,
          goal: prompt,
          status: 'completed',
          tasks: [
            { id: 't1', tool: 'read_screen', parameters: {}, status: 'completed', duration: 0.32 }
          ]
        });
      } else if (lower.includes("search") || lower.includes("browser")) {
        responseText = "🌐 Web search query executed via Autonomous Browser Agent.";
        store.setWorkflow({
          workflowId: `wf_${Date.now()}`,
          goal: prompt,
          status: 'completed',
          tasks: [
            { id: 't1', tool: 'search_web', parameters: { query: prompt }, status: 'completed', duration: 0.45 }
          ]
        });
      } else {
        responseText = `I have processed your query: "${prompt}". All local engines operational.`;
      }

      store.addMessage({ role: 'assistant', content: responseText });
      store.addDevLog('WORKFLOW_COMPLETED', { goal: prompt, response: responseText });
    }, 600);
  }
}

export const auraAPI = AuraAPIService.getInstance();
