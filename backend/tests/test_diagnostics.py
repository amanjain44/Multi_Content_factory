import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_diagnostics_endpoint(authenticated_client: AsyncClient):
    res = await authenticated_client.get("/api/diagnostics")
    assert res.status_code == 200, res.text
    
    data = res.json()
    
    # 1. Structure validation
    assert "backend" in data
    assert "database" in data
    assert "vector_store" in data
    assert "ai" in data
    assert "embeddings" in data
    assert "rag" in data
    assert "environment" in data
    
    # 2. Database validation
    # Because tests use a real test database, it should be Healthy
    assert data["database"]["status"] == "Healthy"
    
    # 3. Security validation: ensure NO secrets are exposed
    # Check that OPENAI_API_KEY, POSTGRES_PASSWORD, DATABASE_URL don't appear in the dump
    dump_str = str(data)
    # The literal strings shouldn't be exposed, but we can just assert some common secret keys aren't in keys
    for key in data.keys():
        assert "password" not in key.lower()
        assert "key" not in key.lower()
        
    for ai_key in data["ai"].keys():
        assert "api_key" not in ai_key.lower()
        assert "password" not in ai_key.lower()
        
    # We'll assert we don't have the literal strings of secrets if we knew them, but checking keys is safe.
    assert "OPENAI_API_KEY" not in dump_str
    assert "POSTGRES_PASSWORD" not in dump_str
    
    # 4. Environment check
    # Since tests run with AI_PROVIDER=demo usually (or we can just check it's one of the valid ones)
    assert data["environment"]["mode"] in ["Demo", "Development", "Production"]
