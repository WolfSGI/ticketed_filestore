import pytest
import re
import uuid
from typing import Iterator
from unittest import mock

import pytest
from ticketed_filestore.meta import FileInfo, FileMetadata
from ticketed_filestore.memory import MemoryStorage
from unittest import mock


def mock_uuid():
    return uuid.UUID(int=0x12345678123456781234567812345678)


@mock.patch('uuid.uuid4', mock_uuid)
def test_memory_store(test_file):
    storage = MemoryStorage('memory')
    info = storage.store(test_file)
    assert isinstance(info, FileInfo)
    assert info.metadata == FileMetadata(
        namespace='flat',
        size=28,
        checksums={'md5': '53195454e1210adae36ecb34453a1f5a'},
    )


@mock.patch('uuid.uuid4', mock_uuid)
def test_memory_store_metadata(test_file):
    storage = MemoryStorage('memory')
    storage_info = storage.store(
        test_file, filename="test.jpg", owner="admin")
    assert storage_info.metadata == FileMetadata(
        namespace='flat',
        size=28,
        filename='test.jpg',
        owner='admin',
        checksums={
            'md5': '53195454e1210adae36ecb34453a1f5a'
        },
    )


@mock.patch('uuid.uuid4', mock_uuid)
def test_memory_store_conflicting_metadata(test_file):
    storage = MemoryStorage('memory')
    with pytest.raises(TypeError):
        storage_info = storage.store(test_file, size=12)


def test_memory_get(test_file):
    storage = MemoryStorage('memory')
    storage_info = storage.store(test_file)
    iterator = storage.stream(storage_info.ticket)
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()


def test_memory_delete(test_file):
    storage = MemoryStorage('memory')
    storage_info = storage.store(test_file)
    storage.delete(storage_info.ticket)

    with pytest.raises(FileNotFoundError):
        storage.delete(storage_info.ticket)


def test_memory_checksum(test_file, tmp_path):
    storage = MemoryStorage('memory')
    storage_info = storage.store(test_file)
    assert storage_info.metadata['checksums'] == {
        'sha256':
        '18e9b7c9c1be46b1c62938b11b02f513a4d507630c4aee744799df83e0a94ba6'
    }

    with pytest.raises(LookupError) as exc:
        MemoryStorage('memory', algorithm="pouet")
    assert str(exc.value) == "Unknown algorithm: `pouet`."
