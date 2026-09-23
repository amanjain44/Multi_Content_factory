"use client"

import React, { useState, useEffect } from 'react';
import { ContentOpportunity } from '@/types/workflow';
import { ContentSelectionService } from '@/lib/services/content-selection.service';
import { ProjectService } from '@/lib/project-service';
import { Project, WorkflowStage } from '@/types/project';
import { Sparkles, Check, ArrowRight, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  project: Project;
  activeStage: WorkflowStage;
  onComplete: () => void;
}

export function ContentSelectionStage({ project, activeStage, onComplete }: Props) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [opportunities, setOpportunities] = useState<ContentOpportunity[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Restore persisted data when stage already has generated results
  useEffect(() => {
    if (activeStage.data?.opportunities) {
      setOpportunities(activeStage.data.opportunities);
      if (activeStage.data?.selectedId) {
        setSelectedId(activeStage.data.selectedId);
      }
    }
  }, [activeStage]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      // Call the real AI endpoint (demo or OpenAI depending on AI_PROVIDER env)
      const results = await ContentSelectionService.generateOpportunities(project.id);
      setOpportunities(results);

      // Persist the generated opportunities immediately via PostgreSQL
      await ProjectService.updateWorkflowStage(project.id, activeStage.id, {
        data: { ...activeStage.data, opportunities: results },
      });
    } catch (err: any) {
      setError(err.message || 'AI generation failed. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSelect = async (id: string) => {
    setSelectedId(id);
    // Persist selection to PostgreSQL immediately
    await ProjectService.updateWorkflowStage(project.id, activeStage.id, {
      data: { ...activeStage.data, opportunities, selectedId: id },
    });
  };

  const handleConfirm = () => {
    if (selectedId) {
      onComplete();
    }
  };

  // ── Empty state: prompt the user to generate ──────────────────────────────
  if (opportunities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[50vh] space-y-6 text-center">
        <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-2 text-primary">
          <Sparkles className="w-8 h-8" />
        </div>
        <div className="max-w-md">
          <h3 className="text-2xl font-bold text-foreground mb-2">Extract Content Opportunities</h3>
          <p className="text-muted-foreground text-sm mb-8">
            The AI will analyze your source material ({project.sourceType}) and extract the most
            valuable angles and content formats for your audience.
          </p>

          {/* Error banner with retry */}
          {error && (
            <div className="flex items-start gap-3 p-4 mb-6 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm text-left">
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
              <div className="flex-1">
                <p className="font-semibold mb-1">Generation failed</p>
                <p className="text-red-400/90">{error}</p>
              </div>
            </div>
          )}

          <button
            id="btn-generate-content-selection"
            onClick={handleGenerate}
            disabled={isGenerating}
            className="inline-flex items-center justify-center gap-2 h-12 px-8 rounded-full bg-foreground text-background font-semibold hover:scale-[1.02] active:scale-95 transition-all shadow-md w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>AI is analyzing your source material...</span>
              </>
            ) : error ? (
              <>
                <RefreshCw className="w-5 h-5" />
                <span>Retry Generation</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Analyze &amp; Generate Opportunities</span>
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  // ── Results state: show opportunities ────────────────────────────────────
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-foreground">Select a Content Direction</h3>
          <p className="text-sm text-muted-foreground">
            Based on your source, here are the most promising AI-generated content opportunities.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Allow regeneration even after results are shown */}
          {activeStage.status !== 'Completed' && (
            <button
              id="btn-regenerate-content-selection"
              onClick={handleGenerate}
              disabled={isGenerating}
              title="Regenerate opportunities"
              className="inline-flex items-center gap-1.5 h-9 px-4 rounded-full border border-border/50 text-muted-foreground hover:text-foreground hover:border-border text-xs font-medium transition-all disabled:opacity-50"
            >
              {isGenerating ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <RefreshCw className="w-3.5 h-3.5" />
              )}
              <span>Regenerate</span>
            </button>
          )}

          {selectedId && activeStage.status !== 'Completed' && (
            <button
              id="btn-confirm-content-selection"
              onClick={handleConfirm}
              className="inline-flex items-center gap-2 h-10 px-5 rounded-full bg-primary text-primary-foreground font-medium hover:scale-[1.02] active:scale-95 transition-all shadow-md"
            >
              <span>Confirm Selection</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Inline error in results view */}
      {error && (
        <div className="flex items-start gap-3 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {opportunities.map((opp) => (
          <div
            key={opp.id}
            id={`opportunity-card-${opp.id}`}
            onClick={() => activeStage.status !== 'Completed' && handleSelect(opp.id)}
            className={cn(
              'relative flex flex-col p-6 rounded-2xl border transition-all duration-300 text-left cursor-pointer overflow-hidden group',
              selectedId === opp.id
                ? 'bg-primary/5 border-primary/50 shadow-[0_0_15px_rgba(99,102,241,0.1)] ring-1 ring-primary/20'
                : 'glass-panel hover:border-primary/30 hover:bg-muted/50',
              activeStage.status === 'Completed' &&
                selectedId !== opp.id &&
                'opacity-50 grayscale cursor-default'
            )}
          >
            {/* Selection indicator */}
            <div
              className={cn(
                'absolute top-5 right-5 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors',
                selectedId === opp.id
                  ? 'bg-primary border-primary text-background'
                  : 'border-muted-foreground/30 text-transparent'
              )}
            >
              <Check className="w-3.5 h-3.5" />
            </div>

            <div className="pr-10 mb-4">
              <h4 className="text-lg font-bold text-foreground mb-2 leading-tight">{opp.title}</h4>
              <p className="text-sm text-muted-foreground leading-relaxed">{opp.summary}</p>
            </div>

            <div className="mt-auto space-y-4 pt-4 border-t border-border/50">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-primary mb-1 block">
                  Why it works
                </span>
                <p className="text-sm text-foreground/80">{opp.whyInteresting}</p>
              </div>

              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 block">
                  Key Points
                </span>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {opp.keyPoints.map((point, i) => (
                    <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary/50 mt-1 shrink-0" />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex items-center gap-4 pt-2">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-medium text-muted-foreground">Audience:</span>
                  <span className="text-xs font-semibold text-foreground bg-muted px-2 py-0.5 rounded-full">
                    {opp.potentialAudience}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
