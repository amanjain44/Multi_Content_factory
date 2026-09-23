from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from uuid import UUID
import os
import shutil

from ...db.session import get_db
from ...models.source import SourceDocument
from ...services.project_service import ProjectService
from ...services.ingestion_service import IngestionService
from ...ai.config import AIConfig
from ...api.deps import get_current_user

router = APIRouter()

def _get_ai_config() -> AIConfig:
    from ...core.config import settings
    return AIConfig(
        provider=settings.AI_PROVIDER,
        api_key=settings.OPENAI_API_KEY,
        model_name=settings.AI_MODEL_NAME,
        temperature=settings.AI_TEMPERATURE
    )

@router.post("/{project_id}/sources/ingest", response_model=Dict[str, Any])
async def ingest_source(
    project_id: str,
    background_tasks: BackgroundTasks,
    source_type: str = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Ingest a source document for a project (URL, Text, or PDF File).
    """
    try:
        project_uuid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid project_id format")

    project_service = ProjectService(db, current_user.id)
    project = await project_service.get_project(project_uuid)
    # Automatically raises 404 if project not found

    config = _get_ai_config()
    
    # Process inputs based on type
    file_path = None
    url = None
    text = None
    
    if source_type == "url":
        if not content:
            raise HTTPException(status_code=400, detail="URL content is required")
        url = content
    elif source_type == "text":
        if not content:
            raise HTTPException(status_code=400, detail="Text content is required")
        text = content
    elif source_type == "pdf":
        if not file:
            raise HTTPException(status_code=400, detail="PDF file is required")
            
        # Save uploaded file to a temporary location
        temp_dir = os.path.join(os.getcwd(), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, file.filename)
        content_bytes = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content_bytes)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")

    try:
        # Create SourceDocument first
        metadata = {}
        source_url = None
        if source_type == "url":
            source_url = url
        elif source_type == "text":
            metadata["raw_text"] = text
        elif source_type == "pdf" and file_path:
            metadata["file_path"] = file_path

        source_doc = SourceDocument(
            project_id=project_uuid,
            source_type=source_type if source_type != "pdf" else "upload",
            name=f"Ingested {source_type}",
            source_url=source_url,
            metadata_=metadata
        )
        db.add(source_doc)
        await db.commit()
        await db.refresh(source_doc)

        source = await IngestionService.ingest_source(
            db=db,
            project_id=project_uuid,
            source_id=source_doc.id,
            config=config
        )
        
        # Clean up file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            
        from sqlalchemy import select, func
        from ...models.source import DocumentChunk
        chunks_created = await db.scalar(
            select(func.count(DocumentChunk.id))
            .where(DocumentChunk.source_document_id == source.id)
        )

        return {
            "id": str(source.id),
            "project_id": str(source.project_id),
            "source_type": source.source_type,
            "title": source.name,
            "status": "Success",
            "message": f"Successfully ingested {source_type}",
            "chunks_created": chunks_created or 0
        }
    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        # Note user requirement: Never silently return fake success for real ingestion failures.
        raise HTTPException(status_code=500, detail=f"Failed to ingest source: {repr(e)}")
