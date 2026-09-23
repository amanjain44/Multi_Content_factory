import uuid
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text

from app.models.source import DocumentChunk
from app.ai.providers.embedding.base import BaseEmbeddingProvider
from app.ai.providers.embedding.factory import EmbeddingProviderFactory
from app.ai.config import AIConfig

class RetrievedChunk:
    def __init__(self, content: str, score: float, source_document_id: str, chunk_id: str, metadata: Dict[str, Any]):
        self.content = content
        self.score = score
        self.source_document_id = source_document_id
        self.chunk_id = chunk_id
        self.metadata = metadata

class RetrievalService:
    @staticmethod
    async def retrieve(
        db: AsyncSession,
        project_id: uuid.UUID,
        query: str,
        config: AIConfig,
        top_k: int = 5
    ) -> List[RetrievedChunk]:
        """
        Embeds the query and performs a similarity search on DocumentChunks for the given project.
        """
        if not query.strip():
            return []

        # 1. Embed query
        embedding_provider = EmbeddingProviderFactory.get_provider(config)
        query_embedding = await embedding_provider.embed_text(query)
        
        if not query_embedding or sum(query_embedding) == 0:
            # Fallback if demo embedding couldn't embed anything useful
            return []

        # 2. Search pgvector
        # Cosine distance operator is <=>. To order by similarity, we order by distance ASC.
        # Score conceptually is 1 - distance.
        stmt = (
            select(DocumentChunk, DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"))
            .where(DocumentChunk.project_id == project_id)
            .order_by("distance")
            .limit(top_k)
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        retrieved_chunks = []
        for chunk, distance in rows:
            score = 1.0 - distance
            retrieved_chunks.append(RetrievedChunk(
                content=chunk.content,
                score=score,
                source_document_id=str(chunk.source_document_id),
                chunk_id=str(chunk.id),
                metadata=chunk.metadata_ or {}
            ))
            
        return retrieved_chunks
