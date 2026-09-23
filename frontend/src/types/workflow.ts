export interface ContentOpportunity {
  id: string;
  title: string;
  summary: string;
  whyInteresting: string;
  keyPoints: string[];
  potentialAudience: string;
  estimatedValue: string;
}

export interface PlatformRecommendation {
  id: string;
  projectId: string;
  platform: 'LinkedIn' | 'Twitter/X' | 'Blog' | 'Newsletter' | 'Instagram' | 'YouTube';
  suitability: number; // 0-100
  reasoning: string;
  recommendedFormat: string;
  recommendedLength: string;
  audience: string;
  tone: string;
  priority: 'Recommended' | 'Optional';
  selected?: boolean;
}

export interface TopicAngle {
  id: string;
  projectId: string;
  title: string;
  angle: string;
  hook: string;
  description: string;
  targetAudience: string;
  corePromise: string;
  differentiation: string;
  supportingPoints: string[];
  recommendedPlatforms: string[];
  selected?: boolean;
}

export interface PlatformAdaptation {
  platform: string;
  format: string;
  notes: string;
}

export interface ContentStrategy {
  id: string;
  projectId: string;
  objective: string;
  targetAudience: string;
  coreMessage: string;
  valueProposition: string;
  tone: string;
  format: string;
  hookStrategy: string;
  keyTalkingPoints: string[];
  callToAction: string;
  contentStructure: string;
  platformAdaptations: PlatformAdaptation[];
  selected?: boolean;
}

export interface StoryboardScene {
  id: string;
  order: number;
  title: string;
  purpose: string;
  narration: string;
  visualDirection: string;
  onScreenText: string;
  transition: string;
  estimatedDuration: string;
}

export interface Storyboard {
  id: string;
  projectId: string;
  title: string;
  objective: string;
  status: 'Draft' | 'Needs Review' | 'Approved';
  scenes: StoryboardScene[];
}

export interface ScriptSection {
  id: string;
  order: number;
  title: string;
  narration: string;
  visualNotes: string;
  onScreenText: string;
  estimatedDuration: string;
}

export interface Script {
  id: string;
  projectId: string;
  title: string;
  platform: string;
  format: string;
  hook: string;
  conclusion: string;
  callToAction: string;
  status: 'Draft' | 'Needs Review' | 'Approved';
  sections: ScriptSection[];
}
