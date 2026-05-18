import pytest
import re
import uuid
from typing import Iterator
from unittest import mock

import pytest
from ticketed_filestore.meta import FileInfo
from ticketed_filestore.fs import BushyStorage, FlatStorage
from unittest import mock


def mock_uuid():
    return uuid.UUID(int=0x12345678123456781234567812345678)


@mock.patch('uuid.uuid4', mock_uuid)
def test_fs_flat_store(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    storage_info = storage.store(test_file)
    assert storage_info == FileInfo(
        namespace='flat',
        ticket='12345678-1234-5678-1234-567812345678',
        size=28,
        checksum=('md5', '53195454e1210adae36ecb34453a1f5a'),
        metadata={}
    )


def test_fs_flat_get(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    storage_info = storage.store(test_file)
    iterator = storage.get(storage_info['ticket'])
    assert isinstance(iterator, Iterator)
    test_file.seek(0)
    assert b''.join(iterator) == test_file.read()


def test_fs_flat_delete(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path)
    storage_info = storage.store(test_file)
    storage.delete(storage_info['ticket'])

    with pytest.raises(FileNotFoundError):
        storage.delete(storage_info['ticket'])


def test_fs_flat_checksum(test_file, tmp_path):
    storage = FlatStorage('flat', tmp_path, algorithm="sha256")
    storage_info = storage.store(test_file)
    assert storage_info['checksum'] == (
        'sha256',
        '18e9b7c9c1be46b1c62938b11b02f513a4d507630c4aee744799df83e0a94ba6'
    )

    with pytest.raises(LookupError) as exc:
        FlatStorage('flat', tmp_path, algorithm="pouet")
    assert str(exc.value) == "Unknown algorithm: `pouet`."
