import pytest

from app import app

@pytest.fixture
def client():
    # Set up the Flask test client
    with app.test_client() as client:
        yield client