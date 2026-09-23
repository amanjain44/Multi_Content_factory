import { Storyboard } from '@/types/workflow';
import { apiClient } from '@/lib/api-client';

export const StoryboardService = {
  /**
   * Calls the backend AI endpoint to generate a storyboard.
   *
   * The backend reads all required context from PostgreSQL automatically:
   * - content-selection stage  (selected opportunity)
   * - platform-strategy stage  (selected platforms)
   * - topic-angle stage        (selected angle)
   * - content-strategy stage   (approved strategy)
   *
   * Works in DEMO mode (AI_PROVIDER=demo) without an API key.
   * Works in OPENAI mode (AI_PROVIDER=openai) with a real API call.
   *
   * @param projectId - The project UUID
   * @returns A Storyboard object ready for human review and editing
   * @throws Error with descriptive message on failure
   */
  generateStoryboard: async (projectId: string): Promise<Storyboard> => {
    try {
      const data = await apiClient.post('/ai/storyboard', {
        projectId,
      });

      // The backend returns { storyboard: { ... } }
      const storyboard: Storyboard = data.storyboard;

      if (!storyboard) {
        throw new Error('AI returned no storyboard data. Please try again.');
      }

      if (!Array.isArray(storyboard.scenes) || storyboard.scenes.length === 0) {
        throw new Error('AI returned a storyboard with no scenes. Please try again.');
      }

      return storyboard;
    } catch (error: any) {
      // Re-throw with a user-friendly message
      if (error.message?.includes('API Error: 400')) {
        throw new Error(
          'Prerequisite stages are missing. Ensure Content Selection, Platform Strategy, Topic & Angle, and Content Strategy are all completed before generating a storyboard.'
        );
      }
      if (error.message?.includes('API Error: 404')) {
        throw new Error('Project not found. Please refresh and try again.');
      }
      if (error.message?.includes('API Error: 500')) {
        throw new Error(
          'AI storyboard generation failed on the server. Check your AI provider configuration or try again.'
        );
      }
      if (error.message?.includes('API Error: 422')) {
        throw new Error('Invalid request. Please refresh the page and try again.');
      }
      throw error;
    }
  },
};
