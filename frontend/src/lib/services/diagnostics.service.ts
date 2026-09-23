import { apiClient } from '../api-client';

export interface BackendDiagnostic {
  status: 'Healthy' | 'Degraded' | 'Unavailable' | 'Not configured' | 'Ready' | 'Enabled';
  message?: string;
}

export interface DatabaseDiagnostic {
  status: 'Healthy' | 'Degraded' | 'Unavailable' | 'Not configured' | 'Ready' | 'Enabled';
  message?: string;
}

export interface VectorStoreDiagnostic {
  status: 'Healthy' | 'Degraded' | 'Unavailable' | 'Not configured' | 'Ready' | 'Enabled';
  extension?: string;
  message?: string;
}

export interface AIDiagnostic {
  status: 'Healthy' | 'Degraded' | 'Unavailable' | 'Not configured' | 'Ready' | 'Enabled';
  provider: string;
  model: string;
  message?: string;
}

export interface EmbeddingDiagnostic {
  status: 'Healthy' | 'Degraded' | 'Unavailable' | 'Not configured' | 'Ready' | 'Enabled';
  provider: string;
  message?: string;
}

export interface RAGDiagnostic {
  status: 'Healthy' | 'Degraded' | 'Unavailable' | 'Not configured' | 'Ready' | 'Enabled';
  message?: string;
}

export interface EnvironmentDiagnostic {
  mode: string;
  message?: string;
}

export interface DiagnosticsResponse {
  backend: BackendDiagnostic;
  database: DatabaseDiagnostic;
  vectorStore: VectorStoreDiagnostic;
  ai: AIDiagnostic;
  embeddings: EmbeddingDiagnostic;
  rag: RAGDiagnostic;
  environment: EnvironmentDiagnostic;
}

export const DiagnosticsService = {
  async getDiagnostics(): Promise<DiagnosticsResponse> {
    return apiClient.get('/diagnostics/');
  }
};
