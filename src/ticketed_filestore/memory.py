import re
import uuid
from io import BytesIO
from abc import ABC
from typing import Iterator, Iterable, BinaryIO
from .meta import FileInfo, FileMetadata, Storage, ChecksumAlgorithm


class MemoryStorage(Storage, ABC):

    checksum_algorithm: ChecksumAlgorithm

    def __init__(self, namespace: str, algorithm='md5'):
        self.namespace = namespace
        self._store = {}
        try:
            self.checksum_algorithm = ChecksumAlgorithm[algorithm]
        except KeyError:
            raise LookupError(f'Unknown algorithm: `{algorithm}`.')

    def to_uri(self, ticket: str) -> None:
        return None

    def new_ticket(self) -> str:
        return str(uuid.uuid4())

    @staticmethod
    def file_iterator(file_: BinaryIO, chunk=4096) -> Iterator[bytes]:
        with file_ as reader:
            while True:
                data = reader.read(chunk)
                if not data:
                    break
                yield data

    def stream(self, ticket: str) -> Iterator[bytes]:
        bio = self._store.get(ticket)
        if bio is None:
            raise FileNotFoundError(f"File {ticket} is unknown.")
        return self.file_iterator(bio)

    def __contains__(self, ticket: str) -> bool:
        return ticket in self._store

    def store(
            self,
            data: BinaryIO | Iterable[bytes],
            ticket: str = None,
            **metadata
    ) -> FileInfo:
        if ticket is None:
            ticket = self.new_ticket()
        size = 0
        fhash = self.checksum_algorithm.value()
        target = BytesIO()
        if isinstance(data, BinaryIO):
            iterable = self.file_iterator(data)
        else:
            iterable = data
        for block in iterable:
            size += target.write(block)
            fhash.update(block)

        target.seek(0)
        self._store[ticket] = target
        return FileInfo(
            ticket=ticket,
            metadata=FileMetadata(
                namespace=self.namespace,
                size=size,
                checksums={
                    fhash.name: fhash.hexdigest()
                },
                **metadata,
            )
        )

    def delete(self, ticket: str) -> Iterable[bytes]:
        if ticket not in self._store:
            raise FileNotFoundError(f'Unknown file {ticket}.')
        del self._store[ticket]
