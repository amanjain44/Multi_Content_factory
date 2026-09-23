from typing import Any, Type
from pydantic import BaseModel
from .base import BaseAIProvider
import os

class OpenAIProvider(BaseAIProvider):
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7, api_key: str | None = None):
        from langchain_openai import ChatOpenAI
        
        # Will fallback to os.environ["OPENAI_API_KEY"] if api_key is None
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )

    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> Any:
        structured_llm = self.llm.with_structured_output(schema)
        result = await structured_llm.ainvoke(prompt)
        return result

    async def generate_text(self, prompt: str) -> str:
        response = await self.llm.ainvoke(prompt)
        return response.content
