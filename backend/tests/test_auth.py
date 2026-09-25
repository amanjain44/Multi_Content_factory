import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select
import time
import secrets

@pytest.mark.asyncio
async def test_forgot_password_unknown_email(authenticated_client: AsyncClient):
    # unknown email reset request returns same generic response
    response = await authenticated_client.post("/api/auth/forgot-password", json={"email": "unknown@example.com"})
    assert response.status_code == 200
    assert response.json()["message"] == "If an account exists for this email, a password reset link has been sent."

@pytest.mark.asyncio
async def test_forgot_password_registered_email(authenticated_client: AsyncClient, test_user: User, db_session):
    # registered email reset request
    response = await authenticated_client.post("/api/auth/forgot-password", json={"email": test_user.email})
    assert response.status_code == 200
    assert response.json()["message"] == "If an account exists for this email, a password reset link has been sent."
    
    await db_session.refresh(test_user)
    assert test_user.password_reset_token is not None
    assert test_user.password_reset_expires_at is not None

@pytest.mark.asyncio
async def test_forgot_password_rate_limit(authenticated_client: AsyncClient, test_user: User, db_session):
    # Set request time to 10 seconds ago
    test_user.password_reset_requested_at = int(time.time()) - 10
    await db_session.commit()
    
    # Request again
    response = await authenticated_client.post("/api/auth/forgot-password", json={"email": test_user.email})
    assert response.status_code == 200
    
    await db_session.refresh(test_user)
    # The requested_at should NOT update because of rate limit
    assert test_user.password_reset_requested_at < int(time.time()) - 5

@pytest.mark.asyncio
async def test_reset_password_invalid_token_format(authenticated_client: AsyncClient):
    # invalid token
    response = await authenticated_client.post("/api/auth/reset-password", json={
        "token": "invalidformat",
        "new_password": "newpassword123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token format"

@pytest.mark.asyncio
async def test_reset_password_invalid_token(authenticated_client: AsyncClient, test_user: User, db_session):
    # token string has valid format but incorrect token
    response = await authenticated_client.post("/api/auth/reset-password", json={
        "token": f"{test_user.id}:wrongtoken",
        "new_password": "newpassword123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"

@pytest.mark.asyncio
async def test_reset_password_expired_token(authenticated_client: AsyncClient, test_user: User, db_session):
    # expired token
    raw_token = secrets.token_urlsafe(32)
    test_user.password_reset_token = get_password_hash(raw_token)
    test_user.password_reset_expires_at = int(time.time()) - 100 # expired
    await db_session.commit()
    
    response = await authenticated_client.post("/api/auth/reset-password", json={
        "token": f"{test_user.id}:{raw_token}",
        "new_password": "newpassword123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Token has expired"

@pytest.mark.asyncio
async def test_reset_password_success(authenticated_client: AsyncClient, test_user: User, db_session):
    raw_token = secrets.token_urlsafe(32)
    test_user.password_reset_token = get_password_hash(raw_token)
    test_user.password_reset_expires_at = int(time.time()) + 1000
    await db_session.commit()
    
    # successful password reset
    response = await authenticated_client.post("/api/auth/reset-password", json={
        "token": f"{test_user.id}:{raw_token}",
        "new_password": "newpassword123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successfully."
    
    await db_session.refresh(test_user)
    assert test_user.password_reset_token is None # used token is cleared
    
    # new password succeeds afterward
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/auth/login/access-token", data={
            "username": test_user.email,
            "password": "newpassword123"
        })
        assert login_res.status_code == 200
        
        # old password fails afterward
        login_fail_res = await ac.post("/api/auth/login/access-token", data={
            "username": test_user.email,
            "password": "testpassword" # The default in conftest is usually "testpassword"
        })
        assert login_fail_res.status_code == 400

@pytest.mark.asyncio
async def test_reset_password_used_token(authenticated_client: AsyncClient, test_user: User, db_session):
    # reset token cannot be reused
    # (Since we just cleared it in the previous test, or we can set it to None manually)
    test_user.password_reset_token = None
    await db_session.commit()
    
    response = await authenticated_client.post("/api/auth/reset-password", json={
        "token": f"{test_user.id}:someresettoken",
        "new_password": "newpassword123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"
