from abc import ABC, abstractmethod
from typing import Any, Type
from pydantic import BaseModel

class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> Any:
        """Generate structured output matching the provided Pydantic schema."""
        pass

    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Generate plain text output."""
        pass
