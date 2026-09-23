from .base import BaseAIProvider
from .demo_provider import DemoProvider
from .openai_provider import OpenAIProvider
from ..config import AIConfig

class AIProviderFactory:
    @staticmethod
    def get_provider(config: AIConfig) -> BaseAIProvider:
        if config.provider.lower() == "openai":
            if not config.api_key:
                raise ValueError("OPENAI_API_KEY is required when using the 'openai' provider.")
            return OpenAIProvider(
                model_name=config.model_name,
                temperature=config.temperature,
                api_key=config.api_key
            )
        
        # Default fallback
        return DemoProvider()
