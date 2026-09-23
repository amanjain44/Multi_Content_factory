"use client"

import React from 'react';
import { WorkflowStage, Project } from '@/types/project';
import { Bot, Edit3, FileText, ArrowRight } from 'lucide-react';
import { ContentSelectionStage } from './stages/content-selection-stage';
import { PlatformStrategyStage } from './stages/platform-strategy-stage';
import { TopicAngleStage } from './stages/topic-angle-stage';
import { ContentStrategyStage } from './stages/content-strategy-stage';
import { StoryboardStage } from './stages/storyboard-stage';
import { ScriptStage } from './stages/script-stage';
import { ScheduleDialog } from '@/components/schedule-dialog';
import { Calendar } from 'lucide-react';

interface WorkspaceContentProps {
  project: Project;
  activeStage: WorkflowStage;
  onAdvanceStage: () => void;
}

export function WorkspaceContent({ project, activeStage, onAdvanceStage }: WorkspaceContentProps) {
  const [isScheduleOpen, setIsScheduleOpen] = React.useState(false);

  const renderStageContent = () => {
    switch (activeStage.type) {
      case 'content-selection':
        return (
          <ContentSelectionStage 
            project={project} 
            activeStage={activeStage} 
            onComplete={onAdvanceStage} 
          />
        );
      case 'platform-strategy':
        return (
          <PlatformStrategyStage 
            project={project} 
            activeStage={activeStage} 
            onComplete={onAdvanceStage} 
          />
        );
      case 'topic-angle':
        return (
          <TopicAngleStage 
            project={project} 
            activeStage={activeStage} 
            onComplete={onAdvanceStage} 
          />
        );
      case 'content-strategy':
        return (
          <ContentStrategyStage 
            project={project} 
            activeStage={activeStage} 
            onComplete={onAdvanceStage} 
          />
        );
      case 'storyboard':
        return (
          <StoryboardStage 
            project={project} 
            activeStage={activeStage} 
            onComplete={onAdvanceStage} 
          />
        );
      case 'final-script':
        return (
          <ScriptStage 
            project={project} 
            activeStage={activeStage} 
            onComplete={onAdvanceStage} 
          />
        );
      case 'source-grounding':
        return (
          <div className="space-y-6">
            <div className="glass-panel p-6 rounded-2xl">
              <h3 className="flex items-center gap-2 text-lg font-semibold mb-4 text-foreground">
                <FileText className="w-5 h-5 text-primary" />
                Source Grounding (Completed)
              </h3>
              <div className="bg-muted/50 p-4 rounded-xl border border-border/50 text-sm text-muted-foreground leading-relaxed h-[200px] overflow-y-auto">
                {`[Demo] Automatically completed. This is where the AI extracts the context from the user's source material.`}
              </div>
            </div>
          </div>
        );
      case 'final-script':
        return (
          <div className="space-y-6 flex items-center justify-center h-full min-h-[40vh]">
            <div className="text-center space-y-4 max-w-md">
              <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6 text-primary">
                <Edit3 className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold text-foreground">Script Generation</h3>
              <p className="text-muted-foreground text-sm">
                The AI will generate the final multi-platform scripts, formatting it perfectly for LinkedIn, Twitter, or Newsletter standards.
              </p>
            </div>
          </div>
        );
      default:
        return (
          <div className="flex items-center justify-center h-full min-h-[40vh] border-2 border-dashed border-border/50 rounded-3xl p-12 text-center bg-background/30">
            <div className="space-y-4 max-w-sm">
              <Bot className="w-12 h-12 text-muted-foreground/50 mx-auto" />
              <h3 className="text-lg font-medium text-foreground">Stage Workspace</h3>
              <p className="text-sm text-muted-foreground">
                This area will host the interactive AI tools and generated content for the <strong>{activeStage.type.split('-').join(' ')}</strong> stage.
              </p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-background overflow-hidden relative z-10">
      
      {/* Workspace Header */}
      <div className="flex items-center justify-between px-8 py-5 border-b border-border/50 glass-panel z-20">
        <div className="flex flex-col">
          <span className="text-xs font-semibold tracking-wider text-primary uppercase mb-1">
            Active Stage
          </span>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">
            {activeStage.type.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
          </h2>
        </div>
        
        <div className="flex items-center gap-3">
          <div className={`px-3 py-1 rounded-full text-xs font-medium border ${
            activeStage.status === 'Completed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 
            activeStage.status === 'In Progress' ? 'bg-primary/10 text-primary border-primary/20' : 
            'bg-muted text-muted-foreground border-border/50'
          }`}>
            {activeStage.status}
          </div>
          
          {activeStage.status !== 'Completed' && (
            <button 
              onClick={onAdvanceStage}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-foreground text-background text-sm font-semibold hover:scale-[1.02] active:scale-95 transition-all shadow-md"
            >
              <span>Approve & Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}

          {(activeStage.type === 'final-script') && activeStage.status === 'Completed' && (
            <button 
              onClick={() => setIsScheduleOpen(true)}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-primary text-primary-foreground text-sm font-semibold hover:scale-[1.02] active:scale-95 transition-all shadow-md"
            >
              <Calendar className="w-4 h-4" />
              <span>Schedule Content</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-8 lg:p-12">
        <div className="max-w-4xl mx-auto">
          {renderStageContent()}
        </div>
      </div>

      <ScheduleDialog
        projectId={project.id}
        isOpen={isScheduleOpen}
        onClose={() => setIsScheduleOpen(false)}
        onScheduled={() => {
          // Additional logic could go here, for now it will just show a toast in the dialog
        }}
      />
    </div>
  );
}
