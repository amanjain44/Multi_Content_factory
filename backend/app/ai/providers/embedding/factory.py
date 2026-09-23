import os
from .base import BaseEmbeddingProvider
from .demo import DemoEmbeddingProvider
from .openai import OpenAIEmbeddingProvider
from app.ai.config import AIConfig

class EmbeddingProviderFactory:
    @staticmethod
    def get_provider(config: AIConfig) -> BaseEmbeddingProvider:
        # Default to demo if not explicitly set, or allow environment override
        embedding_provider = os.getenv("EMBEDDING_PROVIDER", config.provider).lower()
        
        if embedding_provider == "openai":
            if not config.api_key:
                raise ValueError("OPENAI_API_KEY is required when using the 'openai' embedding provider.")
            # Use text-embedding-3-small as default for OpenAI
            model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            return OpenAIEmbeddingProvider(
                model_name=model_name,
                api_key=config.api_key
            )
        
        # Default fallback
        return DemoEmbeddingProvider()
