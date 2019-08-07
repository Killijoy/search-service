import pytest

from falcon import testing

from app import search


@pytest.fixture()
def client():
    return testing.TestClient(search)
