"use client"

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ProjectService, DEFAULT_STAGES } from '@/lib/project-service';
import { Project, ProjectStatus } from '@/types/project';
import { WorkflowSidebar } from '@/components/projects/workflow-sidebar';
import { WorkspaceContent } from '@/components/projects/workspace-content';
import { ArrowLeft, CheckCircle2, Clock, PlayCircle } from 'lucide-react';
import Link from 'next/link';

export default function ProjectWorkspace() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [activeStageId, setActiveStageId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProject = async () => {
      if (id) {
        const p = await ProjectService.getProject(id);
        if (p) {
          setProject(p);
          // Default to the current active stage, or the first stage if none
          const current = p.stages.find((s: any) => s.type === p.currentStage) || p.stages[0];
          if (current) setActiveStageId(current.id);
        }
        setIsLoading(false);
      }
    };
    fetchProject();
  }, [id]);

  const handleStageSelect = (stageId: string) => {
    setActiveStageId(stageId);
  };

  const handleAdvanceStage = async () => {
    if (!project || !activeStageId) return;

    // Mark current stage as complete
    const updated = await ProjectService.updateWorkflowStage(project.id, activeStageId, { status: 'Completed' });
    
    if (updated) {
      const currentIndex = updated.stages.findIndex((s: any) => s.id === activeStageId);
      const nextStage = updated.stages[currentIndex + 1];

      if (nextStage) {
        // Unlock next stage and set to in progress
        const newlyUpdated = await ProjectService.updateWorkflowStage(updated.id, nextStage.id, { status: 'In Progress' });
        if (newlyUpdated) {
          setProject(newlyUpdated);
          setActiveStageId(nextStage.id);
        }
      } else {
        // All stages complete
        const finalProject = await ProjectService.updateProjectStatus(updated.id, 'Completed');
        setProject(finalProject);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[50vh]">
        <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[50vh] p-4 text-center">
        <h2 className="text-3xl font-bold mb-4">Project Not Found</h2>
        <p className="text-muted-foreground mb-8">The project you are looking for does not exist or has been deleted.</p>
        <Link href="/projects" className="inline-flex items-center justify-center px-6 py-3 rounded-full bg-foreground text-background font-medium hover:scale-[1.02] active:scale-95 transition-all">
          Back to Projects
        </Link>
      </div>
    );
  }

  const activeStage = project.stages.find(s => s.id === activeStageId) || project.stages[0];

  const getStatusColor = (status: ProjectStatus) => {
    switch (status) {
      case 'Draft': return 'text-muted-foreground bg-muted';
      case 'In Progress': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      case 'Needs Review': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'Approved': return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
      case 'Completed': return 'text-primary bg-primary/10 border-primary/20';
      case 'Failed': return 'text-red-500 bg-red-500/10 border-red-500/20';
      default: return 'text-muted-foreground bg-muted';
    }
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-6rem)] relative z-10 w-full">
      
      {/* Project Global Header */}
      <div className="shrink-0 flex items-center justify-between px-6 py-4 border-b border-border/50 bg-background/80 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <Link href="/projects" className="p-2 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="h-6 w-px bg-border/50" />
          <div>
            <h1 className="text-lg font-bold tracking-tight text-foreground leading-tight line-clamp-1">{project.title}</h1>
            <p className="text-xs text-muted-foreground line-clamp-1">{project.description}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className={`hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${getStatusColor(project.status)}`}>
            {project.status === 'Completed' ? <CheckCircle2 className="w-3.5 h-3.5" /> : 
             project.status === 'In Progress' ? <PlayCircle className="w-3.5 h-3.5" /> : 
             <Clock className="w-3.5 h-3.5" />}
            <span>{project.status}</span>
          </div>
        </div>
      </div>

      {/* Workspace Body */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        <WorkflowSidebar 
          project={project} 
          onStageSelect={handleStageSelect} 
          activeStageId={activeStageId} 
        />
        
        <WorkspaceContent 
          project={project}
          activeStage={activeStage}
          onAdvanceStage={handleAdvanceStage}
        />
      </div>
    </div>
  );
}
