import enum
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypedDict, BinaryIO, Iterable, Iterator, NamedTuple


ChecksumAlgorithm = enum.Enum(
    'Algorithm', {
        name: getattr(hashlib, name)
        for name in hashlib.algorithms_guaranteed
    }
)


class FileMetadata(TypedDict):
    size: int
    namespace: str
    checksums: dict[str, str]


class FileInfo(NamedTuple):
    ticket: str
    metadata: FileMetadata


class Storage(ABC):
    namespace: str

    @abstractmethod
    def new_ticket(self) -> str:
        """Generate a new and unique ticket in the context of this storage.
        """

    @abstractmethod
    def store(
            self,
            data: BinaryIO | Iterable[bytes],
            ticket: str | None = None,
            **metadata
    ) -> FileInfo:
        """Stores the given data and metadata under a given ticket
        or generates a brand new one.
        """

    @abstractmethod
    def stream(self, ticket: str) -> Iterator[bytes]:
        """Returns a bytes iterator from a resolved ticket.
        It ticket cannot be resolved, an error is raised.
        """

    @abstractmethod
    def delete(self, ticket: str) -> bool:
        """Deletes the data and metadata stored under the given ticket.
        """
