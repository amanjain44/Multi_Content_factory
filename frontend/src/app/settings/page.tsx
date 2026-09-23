'use client';

import { useState, useEffect } from 'react';
import { DiagnosticsService, DiagnosticsResponse } from '@/lib/services/diagnostics.service';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, ShieldCheck, Database, BrainCircuit, Server, Settings2 } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function SettingsPage() {
  const [data, setData] = useState<DiagnosticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const response = await DiagnosticsService.getDiagnostics();
        setData(response);
      } catch (err: any) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadSettings();
  }, []);

  if (loading) {
    return (
      <div className="w-full max-w-5xl mx-auto px-6 md:px-8 py-4 flex justify-center items-center h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="w-full max-w-5xl mx-auto px-6 md:px-8 py-4">
        <Alert variant="destructive" className="bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-500 border border-red-200 dark:border-red-500/20 shadow-sm">
          <AlertTitle>Cannot load settings</AlertTitle>
          <AlertDescription>
            The backend API appears to be offline. Make sure the server is running.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const isDemoMode = data.environment.mode === 'Demo';

  return (
    <div className="w-full max-w-5xl mx-auto px-6 md:px-8 py-4 space-y-10 animate-in fade-in duration-500">
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground mb-2">Application Settings</h1>
        <p className="text-muted-foreground">
          Environment and application configuration. These values are currently read-only and managed via environment variables.
        </p>
      </div>

      {isDemoMode && (
        <Alert className="bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-500 border-amber-200 dark:border-amber-500/20 shadow-sm">
          <AlertTitle className="flex items-center gap-2 font-semibold">
            <ShieldCheck className="w-4 h-4" />
            Demo Mode Active
          </AlertTitle>
          <AlertDescription>
            You are running MCF in Demo Mode. AI features will use deterministic fallback providers and will not require real API keys.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6">
        
        {/* Application & Environment */}
        <Card className="bg-white dark:bg-card border border-slate-200 dark:border-border shadow-sm overflow-hidden">
          <CardHeader className="border-b border-slate-100 dark:border-border pb-5 pt-6 px-6 bg-slate-50/50 dark:bg-muted/30">
            <CardTitle className="flex items-center gap-2 text-xl font-bold">
              <Server className="w-6 h-6 text-primary" />
              Application & Environment
            </CardTitle>
            <CardDescription className="pt-1">Core system environment configuration.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider text-slate-500 dark:text-muted-foreground font-semibold">Environment Mode</Label>
                <Input value={data.environment.mode} readOnly className="bg-slate-50 dark:bg-muted/50 border-slate-200 dark:border-border shadow-sm h-11" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider text-slate-500 dark:text-muted-foreground font-semibold">API Status</Label>
                <Input value={data.backend.status} readOnly className="bg-slate-50 dark:bg-muted/50 border-slate-200 dark:border-border shadow-sm h-11" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Configuration */}
        <Card className="bg-white dark:bg-card border border-slate-200 dark:border-border shadow-sm overflow-hidden">
          <CardHeader className="border-b border-slate-100 dark:border-border pb-5 pt-6 px-6 bg-slate-50/50 dark:bg-muted/30">
            <CardTitle className="flex items-center gap-2 text-xl font-bold">
              <BrainCircuit className="w-6 h-6 text-primary" />
              AI Configuration
            </CardTitle>
            <CardDescription className="pt-1">Language model provider and settings.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider text-slate-500 dark:text-muted-foreground font-semibold">AI Provider</Label>
                <Input value={data.ai.provider} readOnly className="bg-slate-50 dark:bg-muted/50 border-slate-200 dark:border-border shadow-sm h-11" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider text-slate-500 dark:text-muted-foreground font-semibold">Model</Label>
                <Input value={data.ai.model} readOnly className="bg-slate-50 dark:bg-muted/50 border-slate-200 dark:border-border shadow-sm h-11" />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label className="text-xs uppercase tracking-wider text-slate-500 dark:text-muted-foreground font-semibold">API Key (OpenAI)</Label>
                <div className="flex items-center p-3 rounded-lg border border-slate-200 dark:border-border bg-slate-50 dark:bg-muted/50 shadow-sm h-11">
                  {data.ai.provider === 'demo' ? (
                    <span className="text-sm font-semibold text-slate-500 dark:text-muted-foreground flex items-center gap-2">
                      <ShieldCheck className="w-5 h-5" /> Not required for Demo Provider
                    </span>
                  ) : data.ai.status === 'Ready' ? (
                    <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-500 flex items-center gap-2">
                      <ShieldCheck className="w-5 h-5" /> Configured ✓
                    </span>
                  ) : (
                    <span className="text-sm font-semibold text-red-600 dark:text-red-500 flex items-center gap-2">
                      <Settings2 className="w-5 h-5" /> Missing API Key
                    </span>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Source & RAG */}
        <Card className="bg-white dark:bg-card border border-slate-200 dark:border-border shadow-sm overflow-hidden">
          <CardHeader className="border-b border-slate-100 dark:border-border pb-5 pt-6 px-6 bg-slate-50/50 dark:bg-muted/30">
            <CardTitle className="flex items-center gap-2 text-xl font-bold">
              <Database className="w-6 h-6 text-primary" />
              Source & RAG Configuration
            </CardTitle>
            <CardDescription className="pt-1">Vector store and retrieval augmented generation settings.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider text-slate-500 dark:text-muted-foreground font-semibold">Embedding Provider</Label>
                <Input value={data.embeddings.provider} readOnly className="bg-slate-50 dark:bg-muted/50 border-slate-200 dark:border-border shadow-sm h-11" />
              </div>
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wider text-slate-500 dark:text-muted-foreground font-semibold">Vector Store Extension</Label>
                <Input value={data.vectorStore.extension || 'None'} readOnly className="bg-slate-50 dark:bg-muted/50 border-slate-200 dark:border-border shadow-sm h-11" />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label className="text-xs uppercase tracking-wider text-slate-500 dark:text-muted-foreground font-semibold">Retrieval Service Status</Label>
                <Input value={data.rag.status} readOnly className="bg-slate-50 dark:bg-muted/50 border-slate-200 dark:border-border shadow-sm h-11" />
              </div>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
