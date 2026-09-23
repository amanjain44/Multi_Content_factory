import { TopicAngle } from '@/types/workflow';
import { apiClient } from '@/lib/api-client';

export const TopicAngleService = {
  /**
   * Calls the backend API to generate topic angles.
   */
  generateTopicAngles: async (projectId: string, opportunityId: string, platformIds: string[]): Promise<TopicAngle[]> => {
    try {
      const data = await apiClient.post('/ai/topic-angle', {
        projectId,
        opportunityId,
        platformIds
      });

      return data.angles || [];
    } catch (error) {
      console.error("Topic Angle generation failed:", error);
      throw error;
    }
  }
};
