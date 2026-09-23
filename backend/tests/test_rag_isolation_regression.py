import pytest
import uuid
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.source import SourceDocument
from app.models.user import User
from app.services.ingestion_service import IngestionService
from app.services.retrieval_service import RetrievalService
from app.ai.config import AIConfig

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    user = User(email=f"test_rag_{uuid.uuid4()}@example.com", hashed_password="pw", is_active=True)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.mark.asyncio
async def test_rag_isolation(db_session: AsyncSession, test_user: User):
    # 1. Create Project A (AI)
    project_a = Project(title="AI Project", source_type="TEXT", source_reference="N/A", user_id=test_user.id)
    db_session.add(project_a)
    await db_session.commit()
    
    source_a = SourceDocument(
        project_id=project_a.id, 
        source_type="text", 
        name="AI text", 
        metadata_={"raw_text": "AI coding assistants are changing the daily workflow of software engineers, moving them from writing boilerplate to reviewing architecture."}
    )
    db_session.add(source_a)
    await db_session.commit()
    
    # 2. Create Project B (JS)
    project_b = Project(title="JS Project", source_type="text", source_reference="N/A", user_id=test_user.id)
    db_session.add(project_b)
    await db_session.commit()
    
    source_b = SourceDocument(
        project_id=project_b.id, 
        source_type="text", 
        name="JS text", 
        metadata_={"raw_text": "JavaScript is a lightweight, interpreted, or just-in-time compiled programming language with first-class functions."}
    )
    db_session.add(source_b)
    await db_session.commit()
    
    config = AIConfig(provider="demo")
    
    # 3. Ingest both
    await IngestionService.ingest_source(db_session, project_a.id, source_a.id, config)
    await IngestionService.ingest_source(db_session, project_b.id, source_b.id, config)
    
    # 4. Retrieve for B
    chunks_b = await RetrievalService.retrieve(db_session, project_b.id, "javascript", config)
    
    # 5. Assert isolation
    assert len(chunks_b) > 0, "Should retrieve chunks for Project B"
    for chunk in chunks_b:
        assert str(chunk.source_document_id) == str(source_b.id), "Chunk must belong to Project B"
        assert "JavaScript" in chunk.content or "compiled" in chunk.content, "Chunk must contain JS content"
        assert "AI coding" not in chunk.content, "Chunk must NOT contain AI Project content"
