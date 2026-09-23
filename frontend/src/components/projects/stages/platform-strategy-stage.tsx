"use client"

import React, { useState, useEffect } from 'react';
import { PlatformRecommendation } from '@/types/workflow';
import { PlatformStrategyService } from '@/lib/services/platform-strategy.service';
import { ProjectService } from '@/lib/project-service';
import { Project, WorkflowStage } from '@/types/project';
import { Share2, Check, ArrowRight, Loader2, MessageSquare, Video, Mail, FileText, Camera } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  project: Project;
  activeStage: WorkflowStage;
  onComplete: () => void;
}

export function PlatformStrategyStage({ project, activeStage, onComplete }: Props) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [recommendations, setRecommendations] = useState<PlatformRecommendation[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  // Find the selected content opportunity ID from the previous stage
  const prevStage = project.stages.find(s => s.type === 'content-selection');
  const opportunityId = prevStage?.data?.selectedId;

  useEffect(() => {
    if (activeStage.data?.recommendations) {
      setRecommendations(activeStage.data.recommendations);
      if (activeStage.data?.selectedIds) {
        setSelectedIds(activeStage.data.selectedIds);
      }
    }
  }, [activeStage]);

  const handleAnalyze = async () => {
    if (!opportunityId) return;
    
    setIsAnalyzing(true);
    try {
      const results = await PlatformStrategyService.analyzePlatforms(project.id, opportunityId);
      setRecommendations(results);
      
      // Auto-select recommended platforms by default
      const defaultSelected = results.filter(r => r.priority === 'Recommended').map(r => r.id);
      setSelectedIds(defaultSelected);

      await ProjectService.updateWorkflowStage(project.id, activeStage.id, {
        data: { ...activeStage.data, recommendations: results, selectedIds: defaultSelected }
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const toggleSelection = async (id: string) => {
    const newSelected = selectedIds.includes(id) 
      ? selectedIds.filter(i => i !== id)
      : [...selectedIds, id];
    
    setSelectedIds(newSelected);
    
    await ProjectService.updateWorkflowStage(project.id, activeStage.id, {
      data: { ...activeStage.data, recommendations, selectedIds: newSelected }
    });
  };

  const handleConfirm = () => {
    if (selectedIds.length > 0) {
      onComplete();
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'LinkedIn': return <Share2 className="w-5 h-5" />;
      case 'Twitter/X': return <MessageSquare className="w-5 h-5" />;
      case 'YouTube': return <Video className="w-5 h-5" />;
      case 'Newsletter': return <Mail className="w-5 h-5" />;
      case 'Blog': return <FileText className="w-5 h-5" />;
      case 'Instagram': return <Camera className="w-5 h-5" />;
      default: return <Share2 className="w-5 h-5" />;
    }
  };

  if (!opportunityId) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[50vh] text-center">
        <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <Share2 className="w-8 h-8 text-muted-foreground/50" />
        </div>
        <h3 className="text-xl font-semibold mb-2">Stage Locked</h3>
        <p className="text-muted-foreground">You must complete the Content Selection stage first.</p>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[50vh] space-y-6 text-center">
        <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-2 text-primary">
          <Share2 className="w-8 h-8" />
        </div>
        <div className="max-w-md">
          <h3 className="text-2xl font-bold text-foreground mb-2">Platform Strategy</h3>
          <p className="text-muted-foreground text-sm mb-8">
            Based on your selected content, the AI will recommend the best platforms and formats for maximum engagement.
          </p>
          <button 
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="inline-flex items-center justify-center gap-2 h-12 px-8 rounded-full bg-foreground text-background font-semibold hover:scale-[1.02] active:scale-95 transition-all shadow-md w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing Platforms...</span>
              </>
            ) : (
              <>
                <Share2 className="w-5 h-5" />
                <span>Generate Strategy</span>
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-foreground">Select Target Platforms</h3>
          <p className="text-sm text-muted-foreground">Choose one or more platforms to adapt this content for.</p>
        </div>
        
        {selectedIds.length > 0 && activeStage.status !== 'Completed' && (
          <button 
            onClick={handleConfirm}
            className="inline-flex items-center gap-2 h-10 px-5 rounded-full bg-primary text-primary-foreground font-medium hover:scale-[1.02] active:scale-95 transition-all shadow-md shrink-0"
          >
            <span>Confirm Strategy</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {recommendations.map((rec) => {
          const isSelected = selectedIds.includes(rec.id);
          return (
            <div 
              key={rec.id}
              onClick={() => activeStage.status !== 'Completed' && toggleSelection(rec.id)}
              className={cn(
                "relative flex flex-col p-6 rounded-2xl border transition-all duration-300 text-left cursor-pointer overflow-hidden group",
                isSelected 
                  ? "bg-primary/5 border-primary/50 shadow-[0_0_15px_rgba(99,102,241,0.1)] ring-1 ring-primary/20" 
                  : "glass-panel hover:border-primary/30 hover:bg-muted/50",
                activeStage.status === 'Completed' && !isSelected && "opacity-50 grayscale"
              )}
            >
              <div className={cn(
                "absolute top-5 right-5 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors",
                isSelected ? "bg-primary border-primary text-background" : "border-muted-foreground/30 text-transparent"
              )}>
                <Check className="w-3.5 h-3.5" />
              </div>

              <div className="flex items-center gap-3 mb-4">
                <div className={cn(
                  "p-2.5 rounded-xl",
                  isSelected ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground group-hover:text-foreground group-hover:bg-muted/80"
                )}>
                  {getPlatformIcon(rec.platform)}
                </div>
                <div>
                  <h4 className="text-lg font-bold text-foreground leading-tight">{rec.platform}</h4>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={cn(
                      "text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full",
                      rec.priority === 'Recommended' ? "bg-emerald-500/10 text-emerald-500" : "bg-muted text-muted-foreground"
                    )}>
                      {rec.priority}
                    </span>
                    <span className="text-xs text-muted-foreground font-medium">Match: {rec.suitability}%</span>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-foreground/90 leading-relaxed">{rec.reasoning}</p>
              </div>

              <div className="mt-auto space-y-3 pt-4 border-t border-border/50">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Format</span>
                    <span className="text-xs text-foreground font-medium">{rec.recommendedFormat}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Tone</span>
                    <span className="text-xs text-foreground font-medium">{rec.tone}</span>
                  </div>
                </div>
                <div>
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground mb-1 block">Audience</span>
                  <span className="text-xs text-foreground font-medium">{rec.audience}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
