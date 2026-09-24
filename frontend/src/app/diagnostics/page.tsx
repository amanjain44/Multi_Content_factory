'use client';

import { useState, useEffect } from 'react';
import { DiagnosticsService, DiagnosticsResponse } from '@/lib/services/diagnostics.service';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, RefreshCw, CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

export default function DiagnosticsPage() {
  const [data, setData] = useState<DiagnosticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDiagnostics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await DiagnosticsService.getDiagnostics();
      setData(response);
    } catch (err: any) {
      setError(err.message || 'Failed to load diagnostics. Backend may be offline.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDiagnostics();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Healthy':
      case 'Ready':
      case 'Enabled':
        return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
      case 'Degraded':
      case 'Demo':
        return <AlertTriangle className="w-5 h-5 text-amber-500" />;
      case 'Unavailable':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'Not configured':
      default:
        return <Info className="w-5 h-5 text-slate-400 dark:text-muted-foreground" />;
    }
  };

  const getBadgeStyle = (status: string) => {
    switch (status) {
      case 'Healthy':
      case 'Ready':
      case 'Enabled':
        return 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-500 border border-emerald-200 dark:border-emerald-500/20';
      case 'Degraded':
      case 'Demo':
        return 'bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-500 border border-amber-200 dark:border-amber-500/20';
      case 'Unavailable':
        return 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-500 border border-red-200 dark:border-red-500/20';
      case 'Not configured':
      default:
        return 'bg-slate-50 dark:bg-muted text-slate-600 dark:text-muted-foreground border border-slate-200 dark:border-border';
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto px-6 md:px-8 py-4 space-y-10 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground mb-2">System Diagnostics</h1>
          <p className="text-muted-foreground">
            Real-time health and configuration status of the MCF architecture.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={loadDiagnostics} disabled={loading} className="gap-2 bg-white dark:bg-card border border-slate-200 dark:border-border text-slate-700 dark:text-foreground hover:bg-slate-50 dark:hover:bg-muted shadow-sm rounded-full">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            Refresh Diagnostics
          </Button>
          <Button 
            onClick={() => {
              if (confirm('Clear local cache and reset state?')) {
                localStorage.clear();
                sessionStorage.clear();
                window.location.reload();
              }
            }}
            variant="outline" 
            className="gap-2 shadow-sm rounded-full text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
          >
            <RefreshCw className="w-4 h-4" />
            Clear Local Cache & Reset
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-500 border border-red-200 dark:border-red-500/20 shadow-sm rounded-md p-4 flex items-start gap-3">
          <XCircle className="w-5 h-5 mt-0.5" />
          <div>
            <h3 className="font-semibold">Connection Error</h3>
            <p className="text-sm opacity-90">{error}</p>
          </div>
        </div>
      )}

      {loading && !data && (
        <div className="flex justify-center items-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      )}

      {data && (
        <div className="grid gap-6 md:grid-cols-2">
          
          <Card className="bg-white dark:bg-card border border-slate-200 dark:border-border shadow-sm overflow-hidden">
            <CardHeader className="pb-4 pt-6 px-6 border-b border-slate-100 dark:border-border bg-slate-50/50 dark:bg-muted/30">
              <CardTitle className="text-xl font-bold flex items-center gap-2">Core Infrastructure</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 p-6">
              <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-border bg-white dark:bg-card shadow-sm">
                <div className="flex items-center gap-3">
                  {getStatusIcon('Healthy')}
                  <div>
                    <div className="font-semibold text-foreground">Frontend</div>
                    <div className="text-xs text-slate-500 dark:text-muted-foreground">React / Next.js</div>
                  </div>
                </div>
                <div className="font-bold text-xs bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-500 border border-emerald-200 dark:border-emerald-500/20 px-2.5 py-1 rounded-md">Connected</div>
              </div>
              
              <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-border bg-white dark:bg-card shadow-sm">
                <div className="flex items-center gap-3">
                  {getStatusIcon(data.backend.status)}
                  <div>
                    <div className="font-semibold text-foreground">Backend API</div>
                    <div className="text-xs text-slate-500 dark:text-muted-foreground">{data.backend.message}</div>
                  </div>
                </div>
                <div className={`font-bold text-xs ${getBadgeStyle(data.backend.status)} px-2.5 py-1 rounded-md`}>
                  {data.backend.status}
                </div>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-border bg-white dark:bg-card shadow-sm">
                <div className="flex items-center gap-3">
                  {getStatusIcon(data.database.status)}
                  <div>
                    <div className="font-semibold text-foreground">PostgreSQL</div>
                    <div className="text-xs text-slate-500 dark:text-muted-foreground">{data.database.message}</div>
                  </div>
                </div>
                <div className={`font-bold text-xs ${getBadgeStyle(data.database.status)} px-2.5 py-1 rounded-md`}>
                  {data.database.status}
                </div>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-border bg-white dark:bg-card shadow-sm">
                <div className="flex items-center gap-3">
                  {getStatusIcon(data.vectorStore.status)}
                  <div>
                    <div className="font-semibold text-foreground">Vector Store</div>
                    <div className="text-xs text-slate-500 dark:text-muted-foreground">{data.vectorStore.message}</div>
                  </div>
                </div>
                <div className={`font-bold text-xs ${getBadgeStyle(data.vectorStore.status)} px-2.5 py-1 rounded-md`}>
                  {data.vectorStore.status}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white dark:bg-card border border-slate-200 dark:border-border shadow-sm overflow-hidden">
            <CardHeader className="pb-4 pt-6 px-6 border-b border-slate-100 dark:border-border bg-slate-50/50 dark:bg-muted/30">
              <CardTitle className="text-xl font-bold flex items-center gap-2">AI & Data Services</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 p-6">
              <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-border bg-white dark:bg-card shadow-sm">
                <div className="flex items-center gap-3">
                  {getStatusIcon(data.ai.status)}
                  <div>
                    <div className="font-semibold text-foreground">AI Provider ({data.ai.provider})</div>
                    <div className="text-xs text-slate-500 dark:text-muted-foreground">{data.ai.message}</div>
                  </div>
                </div>
                <div className={`font-bold text-xs ${getBadgeStyle(data.ai.status)} px-2.5 py-1 rounded-md`}>
                  {data.ai.status}
                </div>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-border bg-white dark:bg-card shadow-sm">
                <div className="flex items-center gap-3">
                  {getStatusIcon(data.embeddings.status)}
                  <div>
                    <div className="font-semibold text-foreground">Embedding ({data.embeddings.provider})</div>
                    <div className="text-xs text-slate-500 dark:text-muted-foreground">{data.embeddings.message}</div>
                  </div>
                </div>
                <div className={`font-bold text-xs ${getBadgeStyle(data.embeddings.status)} px-2.5 py-1 rounded-md`}>
                  {data.embeddings.status}
                </div>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-border bg-white dark:bg-card shadow-sm">
                <div className="flex items-center gap-3">
                  {getStatusIcon(data.rag.status)}
                  <div>
                    <div className="font-semibold text-foreground">RAG Retrieval</div>
                    <div className="text-xs text-slate-500 dark:text-muted-foreground">{data.rag.message}</div>
                  </div>
                </div>
                <div className={`font-bold text-xs ${getBadgeStyle(data.rag.status)} px-2.5 py-1 rounded-md`}>
                  {data.rag.status}
                </div>
              </div>

              <div className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-border bg-white dark:bg-card shadow-sm">
                <div className="flex items-center gap-3">
                  {getStatusIcon(data.environment.mode === 'Demo' ? 'Demo' : 'Healthy')}
                  <div>
                    <div className="font-semibold text-foreground">Environment</div>
                    <div className="text-xs text-slate-500 dark:text-muted-foreground">{data.environment.message}</div>
                  </div>
                </div>
                <div className={`font-bold text-xs ${getBadgeStyle(data.environment.mode === 'Demo' ? 'Demo' : 'Healthy')} px-2.5 py-1 rounded-md`}>
                  {data.environment.mode} Mode
                </div>
              </div>
            </CardContent>
          </Card>

        </div>
      )}
    </div>
  );
}
