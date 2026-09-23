import { ContentOpportunity } from '@/types/workflow';
import { apiClient } from '@/lib/api-client';

export const ContentSelectionService = {
  /**
   * Calls the backend AI endpoint to generate content opportunities.
   *
   * Uses the configured API base URL (NEXT_PUBLIC_API_URL env var).
   * Works in DEMO mode (no API key required) and OPENAI mode.
   *
   * @param projectId - The project UUID to generate content for
   * @returns Array of ContentOpportunity items
   * @throws Error with descriptive message on failure
   */
  generateOpportunities: async (projectId: string): Promise<ContentOpportunity[]> => {
    try {
      const data = await apiClient.post('/ai/content-selection', {
        projectId,
      });

      const opportunities: ContentOpportunity[] = data.opportunities || [];

      if (!Array.isArray(opportunities) || opportunities.length === 0) {
        throw new Error('AI returned no content opportunities. Please try again.');
      }

      return opportunities;
    } catch (error: any) {
      // Re-throw with a user-friendly message
      if (error.message?.includes('API Error: 404')) {
        throw new Error('Project not found. Please refresh and try again.');
      }
      if (error.message?.includes('API Error: 500')) {
        throw new Error(
          'AI generation failed on the server. Check your AI provider configuration or try again.'
        );
      }
      if (error.message?.includes('API Error: 422')) {
        throw new Error('Invalid request. Please refresh the page and try again.');
      }
      throw error;
    }
  },
};
