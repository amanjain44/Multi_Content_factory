import { Script } from '@/types/workflow';
import { apiClient } from '@/lib/api-client';

export const ScriptService = {
  /**
   * Calls the backend AI endpoint to generate a final script.
   *
   * The backend loads all required context from PostgreSQL automatically:
   * - content-selection stage  (selected opportunity)
   * - platform-strategy stage  (selected platforms)
   * - topic-angle stage        (selected angle)
   * - content-strategy stage   (approved strategy)
   * - storyboard stage         (approved storyboard — MUST be Approved)
   *
   * The script expands each storyboard scene into a complete, platform-adapted
   * script section. Storyboard scene order is preserved exactly.
   *
   * Works in DEMO mode (AI_PROVIDER=demo) without an API key.
   * Works in OPENAI mode (AI_PROVIDER=openai) with a real API call.
   *
   * @param projectId - The project UUID
   * @returns A Script object ready for human review, editing, and approval
   * @throws Error with descriptive message on failure
   */
  generateScript: async (projectId: string): Promise<Script> => {
    try {
      const data = await apiClient.post('/ai/script', {
        projectId,
      });

      // The backend returns { script: { ... } }
      const script: Script = data.script;

      if (!script) {
        throw new Error('AI returned no script data. Please try again.');
      }

      if (!Array.isArray(script.sections) || script.sections.length === 0) {
        throw new Error('AI returned a script with no sections. Please try again.');
      }

      return script;
    } catch (error: any) {
      // Re-throw with user-friendly messages
      if (error.message?.includes('API Error: 400')) {
        throw new Error(
          'Prerequisite stages are missing or the storyboard has not been approved. ' +
          'Ensure Content Selection, Platform Strategy, Topic & Angle, Content Strategy, ' +
          'and an Approved Storyboard are all complete before generating a script.'
        );
      }
      if (error.message?.includes('API Error: 404')) {
        throw new Error('Project not found. Please refresh and try again.');
      }
      if (error.message?.includes('API Error: 500')) {
        throw new Error(
          'AI script generation failed on the server. Check your AI provider configuration or try again.'
        );
      }
      if (error.message?.includes('API Error: 422')) {
        throw new Error('Invalid request. Please refresh the page and try again.');
      }
      throw error;
    }
  },
};
