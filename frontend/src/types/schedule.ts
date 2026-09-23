export interface Schedule {
  id: string;
  projectId: string;
  platform: string;
  scheduledAt: string; // ISO date string
  status: 'Draft' | 'Approved' | 'Scheduled' | 'Completed';
  createdAt: string;
  updatedAt: string;
}

export interface ScheduleWithProject extends Schedule {
  projectTitle: string;
}

export interface CreateScheduleRequest {
  projectId: string;
  platform: string;
  scheduledAt: string;
  status?: string;
}

export interface UpdateScheduleRequest {
  platform?: string;
  scheduledAt?: string;
  status?: string;
}
