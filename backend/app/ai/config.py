from pydantic import BaseModel, Field

class AIConfig(BaseModel):
    provider: str
    api_key: str | None = None
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    timeout: int = 60
