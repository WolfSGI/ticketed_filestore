import pytest
from io import BytesIO


@pytest.fixture(scope="function")
def test_file():
    return BytesIO(b"some initial binary data: \x00\x01")
