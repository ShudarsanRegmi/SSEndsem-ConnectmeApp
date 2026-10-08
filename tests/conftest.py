import os
os.environ["APP_ENV"] = "test"
import pytest
from fastapi.testclient import TestClient
from app.config import settings
settings.APP_ENV = "test"
from app.main import app
from app.database import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def client():
    return TestClient(app)
