import { apiClient } from '../api-client';
import type { Schedule, ScheduleWithProject, CreateScheduleRequest, UpdateScheduleRequest } from '@/types/schedule';

export const ScheduleService = {
  async getSchedules(): Promise<ScheduleWithProject[]> {
    return apiClient.get('/schedules');
  },

  async getSchedule(id: string): Promise<Schedule> {
    return apiClient.get(`/schedules/${id}`);
  },

  async createSchedule(data: CreateScheduleRequest): Promise<Schedule> {
    return apiClient.post('/schedules', data);
  },

  async updateSchedule(id: string, data: UpdateScheduleRequest): Promise<Schedule> {
    return apiClient.put(`/schedules/${id}`, data);
  },

  async deleteSchedule(id: string): Promise<boolean> {
    return apiClient.delete(`/schedules/${id}`);
  },
};
