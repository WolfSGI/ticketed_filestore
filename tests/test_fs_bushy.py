import pytest
import re
import uuid
from typing import Iterator
from unittest import mock

import pytest
from ticketed_filestore.meta import FileInfo, FileMetadata
from ticketed_filestore.fs import BushyStorage
from unittest import mock


def mock_uuid():
    return uuid.UUID(int=0x12345678123456781234567812345678)


@mock.patch('uuid.uuid4', mock_uuid)
def test_fs_bushy_ticket(tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    ticket = storage.new_ticket()
    assert ticket == '12345678-1234-5678-1234-567812345678'


@mock.patch('uuid.uuid4', mock_uuid)
def test_fs_bushy_ticket(tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    ticket = storage.new_ticket()
    path = storage.to_uri(ticket)
    assert path == (
        tmp_path / '1234' / '5678' / '1234-5678-1234-567812345678')

    with pytest.raises(ValueError) as exc:
        storage.to_uri('random ticket')
    assert str(exc.value) == 'Invalid ticket format.'


@mock.patch('uuid.uuid4', mock_uuid)
def test_fs_bushy_store(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    storage_info = storage.store(test_file)
    isinstance(storage_info, FileInfo)

    assert storage_info.metadata == FileMetadata(
        namespace='bushy',
        size=28,
        checksums={
            'md5': '53195454e1210adae36ecb34453a1f5a'
        },
    )


@mock.patch('uuid.uuid4', mock_uuid)
def test_fs_bushy_store_metadata(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    storage_info = storage.store(
        test_file, filename="test.jpg", owner="admin")
    assert storage_info.metadata == FileMetadata(
        namespace='bushy',
        size=28,
        filename='test.jpg',
        owner='admin',
        checksums={
            'md5': '53195454e1210adae36ecb34453a1f5a'
        },
    )


def test_fs_bushy_get(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    storage_info = storage.store(test_file)
    iterator = storage.stream(storage_info.ticket)
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()


def test_fs_bushy_delete(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path)
    storage_info = storage.store(test_file)
    storage.delete(storage_info.ticket)

    with pytest.raises(FileNotFoundError):
        storage.delete(storage_info.ticket)


def test_fs_bushy_checksum(test_file, tmp_path):
    storage = BushyStorage('bushy', tmp_path, algorithm="sha256")
    storage_info = storage.store(test_file)
    assert storage_info.metadata['checksums'] == {
        'sha256':
        '18e9b7c9c1be46b1c62938b11b02f513a4d507630c4aee744799df83e0a94ba6'
    }
    with pytest.raises(LookupError) as exc:
        BushyStorage('bushy', tmp_path, algorithm="pouet")
    assert str(exc.value) == "Unknown algorithm: `pouet`."
