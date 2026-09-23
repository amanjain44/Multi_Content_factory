from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkResult:
    def __init__(self, content: str, chunk_index: int, metadata: Dict[str, Any]):
        self.content = content
        self.chunk_index = chunk_index
        self.metadata = metadata
        self.token_count = len(content.split()) # Approximate

class ChunkingService:
    @staticmethod
    def chunk_text(text: str, base_metadata: Dict[str, Any], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[ChunkResult]:
        if not text:
            return []
            
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = splitter.split_text(text)
        
        results = []
        for i, chunk_content in enumerate(chunks):
            # Shallow copy the base metadata so we don't accidentally mutate it across chunks if we were to add chunk-specific info
            meta = dict(base_metadata)
            meta["chunk_index"] = i
            
            results.append(ChunkResult(
                content=chunk_content,
                chunk_index=i,
                metadata=meta
            ))
            
        return results
