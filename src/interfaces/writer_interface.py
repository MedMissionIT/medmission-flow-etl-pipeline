from abc import ABC, abstractmethod
from typing import Dict, Any, List, Iterator


class DataWriter(ABC):
    @abstractmethod
    def write(self, data: List[Dict[str, Any]], destination: str, mode="w"):
        """Écrit les données dans la destination"""
        pass

    @abstractmethod
    def write_chunked(
        self,
        data_iterator: Iterator[List[Dict[str, Any]]],
        destination: str,
        chunksize: int = 1000,
    ):
        """Écrit les données par morceaux"""
        pass

    @abstractmethod
    def validate_destination(self, destination: str) -> bool:
        """Valide la destination avant écriture"""
        pass
