"""Pytest shared fixtures."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
async def async_client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_lead():
    return {
        "name": "Jane Smith", "company": "TechGiant Corp",
        "email": "jane@techgiant.com", "industry": "Technology",
        "employees": 750, "message": "Need AI automation ASAP, budget approved.",
    }


@pytest.fixture
def sample_email():
    return {
        "subject": "Question about invoice INV-9921",
        "body": "Hi team, I cannot find invoice INV-9921. Can you resend it?",
        "sender": "customer@bigcorp.com",
    }
