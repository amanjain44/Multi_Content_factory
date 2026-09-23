import { PlatformRecommendation } from '@/types/workflow';
import { apiClient } from '@/lib/api-client';

export const PlatformStrategyService = {
  /**
   * Calls the backend API to generate platform recommendations based on the selected opportunity.
   */
  analyzePlatforms: async (projectId: string, opportunityId: string): Promise<PlatformRecommendation[]> => {
    try {
      const data = await apiClient.post('/ai/platform-strategy', {
        projectId,
        opportunityId,
      });

      const recommendations: PlatformRecommendation[] = data.recommendations || [];

      if (!Array.isArray(recommendations) || recommendations.length === 0) {
        throw new Error('AI returned no recommendations. Please try again.');
      }

      return recommendations;
    } catch (error: any) {
      console.error("Platform Strategy generation failed:", error);
      if (error.message?.includes('API Error: 404')) {
        throw new Error('Project or opportunity not found.');
      }
      if (error.message?.includes('API Error: 500')) {
        throw new Error('AI generation failed on the server.');
      }
      throw error;
    }
  }
};
