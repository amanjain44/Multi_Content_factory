import { ContentStrategy } from '@/types/workflow';
import { apiClient } from '@/lib/api-client';

export const ContentStrategyService = {
  /**
   * Calls the backend API to generate content strategy.
   */
  generateStrategy: async (projectId: string, opportunityId: string, platformIds: string[], angleId: string): Promise<ContentStrategy> => {
    try {
      const data = await apiClient.post('/ai/content-strategy', {
        projectId,
        opportunityId,
        platformIds,
        angleId
      });

      return data.strategy;
    } catch (error) {
      console.error("Content Strategy generation failed:", error);
      throw error;
    }
  }
};
