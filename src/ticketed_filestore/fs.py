import re
import uuid
from abc import ABC, abstractmethod
from typing import Iterator, Iterable, BinaryIO
from pathlib import Path
from .meta import FileInfo, Storage, ChecksumAlgorithm


UUID = re.compile(
    "^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


class FilesystemStorage(Storage, ABC):

    checksum_algorithm: ChecksumAlgorithm

    def __init__(self, namespace: str, root: Path, algorithm='md5'):
        self.namespace = namespace
        self.root = root
        try:
            self.checksum_algorithm = ChecksumAlgorithm[algorithm]
        except KeyError:
            raise LookupError(f'Unknown algorithm: `{algorithm}`.')

    @abstractmethod
    def to_uri(self, ticket: str) -> Path | None:
        """Resolves a ticket string into an actual URI.
        This only makes sense if
        """

    def new_ticket(self) -> str:
        return str(uuid.uuid4())

    @staticmethod
    def file_iterator(
            file_: Path | BinaryIO, chunk=4096
    ) -> Iterator[bytes]:
        if isinstance(file_, Path):
            file_ = file_.open('rb')

        with file_ as reader:
            while True:
                data = reader.read(chunk)
                if not data:
                    break
                yield data

    def get(self, ticket: str) -> Iterator[bytes]:
        path = self.to_uri(ticket)
        if not path.exists():
            raise FileNotFoundError(path)
        return self.file_iterator(path)

    def store(self, data: BinaryIO, **metadata) -> FileInfo:
        ticket = self.new_ticket()
        return self.put(ticket, data, **metadata)

    def __contains__(self, ticket: str) -> bool:
        path = self.to_uri(ticket)
        return path.exists()

    def put(
            self,
            ticket: str,
            data: BinaryIO | Iterable[bytes],
            **metadata
    ) -> FileInfo:
        path = self.to_uri(ticket)
        assert not path.exists()  # this happens on ticket conflicts.
        depth = len(path.relative_to(self.root).parents)
        if depth > 1:
            path.parent.mkdir(mode=0o755, parents=True, exist_ok=False)
        size = 0
        fhash = self.checksum_algorithm.value()
        with path.open('wb+') as target:
            if isinstance(data, BinaryIO):
                iterable = self.file_iterator(data)
            else:
                iterable = data
            for block in iterable:
                size += target.write(block)
                fhash.update(block)

        return FileInfo(
            namespace=self.namespace,
            ticket=ticket,
            size=size,
            checksum=(fhash.name, fhash.hexdigest()),
            metadata=metadata
        )

    def delete(self, ticket: str) -> Iterable[bytes]:
        path = self.to_uri(ticket)
        try:
            path.unlink()
            return True
        except FileNotFoundError:
            raise  # we need to propagate.
        return False


class FlatStorage(FilesystemStorage):

    def to_uri(self, uid: str) -> Path:
        return self.root / uid


class BushyStorage(FilesystemStorage):

    def to_uri(self, uid: str) -> Path:
        if not UUID.match(uid):
            raise ValueError('Invalid ticket format.')
        return self.root / uid[0:4] / uid[4:8] / uid[9:]
