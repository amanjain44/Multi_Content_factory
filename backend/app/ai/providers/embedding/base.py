from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single piece of text."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts."""
        pass
