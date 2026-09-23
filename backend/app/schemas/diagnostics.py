from pydantic import BaseModel
from typing import Literal

DiagnosticStatus = Literal["Healthy", "Degraded", "Unavailable", "Not configured", "Ready", "Enabled"]

class BackendDiagnostic(BaseModel):
    status: DiagnosticStatus
    message: str | None = None

class DatabaseDiagnostic(BaseModel):
    status: DiagnosticStatus
    message: str | None = None

class VectorStoreDiagnostic(BaseModel):
    status: DiagnosticStatus
    extension: str | None = None
    message: str | None = None

class AIDiagnostic(BaseModel):
    status: DiagnosticStatus
    provider: str
    model: str
    message: str | None = None

class EmbeddingDiagnostic(BaseModel):
    status: DiagnosticStatus
    provider: str
    message: str | None = None

class RAGDiagnostic(BaseModel):
    status: DiagnosticStatus
    message: str | None = None

class EnvironmentDiagnostic(BaseModel):
    mode: str
    message: str | None = None

class DiagnosticsResponse(BaseModel):
    backend: BackendDiagnostic
    database: DatabaseDiagnostic
    vector_store: VectorStoreDiagnostic
    ai: AIDiagnostic
    embeddings: EmbeddingDiagnostic
    rag: RAGDiagnostic
    environment: EnvironmentDiagnostic
