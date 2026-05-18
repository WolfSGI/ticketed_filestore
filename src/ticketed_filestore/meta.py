import enum
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypedDict, BinaryIO, Iterable


ChecksumAlgorithm = enum.Enum(
    'Algorithm', {
        name: getattr(hashlib, name)
        for name in hashlib.algorithms_guaranteed
    }
)


class FileInfo(TypedDict):
    ticket: str
    size: int
    checksum: tuple[str, str]  # (algorithm, value)
    namespace: str
    metadata: dict | None = None


class Storage(ABC):
    namespace: str

    @abstractmethod
    def new_ticket(self) -> str:
        """Generate a new and unique ticket in the context of this storage.
        """

    @abstractmethod
    def store(self, data: BinaryIO, **metadata) -> FileInfo:
        """Stores the given data and metadata under a brand new ticket.
        """

    @abstractmethod
    def get(self, ticket: str) -> Iterable[bytes]:
        """Returns a bytes iterable from a resolved ticket.
        It ticket cannot be resolved, an error is raised.
        """

    @abstractmethod
    def put(
            self,
            ticket: str,
            data: BinaryIO | Iterable[bytes],
            **metadata
    ) -> FileInfo:
        """Stores the given data and metadata under the provided ticket.
        """

    @abstractmethod
    def delete(self, ticket: str) -> bool:
        """Deletes the data and metadata stored under the given ticket.
        """
