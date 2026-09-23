import { apiClient } from '../api-client';

export const ContentTypeService = {
  generate: async (projectId: string): Promise<any> => {
    try {
      const data = await apiClient.post('/ai/content-type', {
        project_id: projectId
      });
      return data;
    } catch (e) {
      console.error('Failed to generate content type:', e);
      throw e;
    }
  }
};
