import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api")

@pytest.fixture(scope="session")
def api_base_url():
    """API 基础 URL fixture"""
    return API_BASE_URL

@pytest.fixture(scope="session")
def test_token():
    """测试令牌 fixture"""
    return "test_token"

@pytest.fixture(scope="session")
def http_client():
    """HTTP 客户端 fixture"""
    return requests.Session()
