export type ProjectStatus = 'Draft' | 'In Progress' | 'Needs Review' | 'Approved' | 'Completed' | 'Failed';

export type StageStatus = 'Locked' | 'Not Started' | 'In Progress' | 'Completed' | 'Needs Review' | 'Failed';

export type WorkflowStageType = 
  | 'source-grounding'
  | 'content-selection'
  | 'platform-strategy'
  | 'topic-angle'
  | 'content-strategy'
  | 'storyboard'
  | 'final-script'
  | 'review-approval';

export interface WorkflowStage {
  id: string;
  projectId: string;
  type: WorkflowStageType;
  status: StageStatus;
  data?: any;
  createdAt: string;
  updatedAt: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  status: ProjectStatus;
  sourceType: string;
  sourceReference: string;
  currentStage: WorkflowStageType;
  createdAt: string;
  updatedAt: string;
  stages: WorkflowStage[];
}

export interface CreateProjectInput {
  title: string;
  description: string;
  sourceType: string;
  sourceReference: string;
}
