import pytest
import re
import uuid
from typing import Iterator
from unittest import mock

import pytest
from ticketed_filestore.meta import FileInfo, FileMetadata
from ticketed_filestore.fs import BushyStorage, FlatStorage
from unittest import mock


def mock_uuid():
    return uuid.UUID(int=0x12345678123456781234567812345678)


@mock.patch('uuid.uuid4', mock_uuid)
def test_fs_flat_store(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    info = storage.store(test_file)
    assert isinstance(info, FileInfo)
    assert info.metadata == FileMetadata(
        namespace='flat',
        size=28,
        checksums={'md5': '53195454e1210adae36ecb34453a1f5a'},
    )

@mock.patch('uuid.uuid4', mock_uuid)
def test_fs_flat_store_metadata(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
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
def test_fs_flat_store_conflicting_metadata(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    with pytest.raises(TypeError):
        storage_info = storage.store(test_file, size=12)


def test_fs_flat_get(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    storage_info = storage.store(test_file)
    iterator = storage.stream(storage_info.ticket)
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()


def test_fs_flat_delete(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    storage_info = storage.store(test_file)
    storage.delete(storage_info.ticket)

    with pytest.raises(FileNotFoundError):
        storage.delete(storage_info.ticket)


def test_fs_flat_checksum(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path, algorithm="sha256")
    storage_info = storage.store(test_file)
    assert storage_info.metadata['checksums'] == {
        'sha256':
        '18e9b7c9c1be46b1c62938b11b02f513a4d507630c4aee744799df83e0a94ba6'
    }

    with pytest.raises(LookupError) as exc:
        FlatStorage('flat', tmp_path, algorithm="pouet")
    assert str(exc.value) == "Unknown algorithm: `pouet`."
