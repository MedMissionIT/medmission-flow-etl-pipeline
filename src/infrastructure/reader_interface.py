from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any


class DataReader(ABC):
    @abstractmethod
    def read(self, source: str) -> Iterator[Dict[str, Any]]:
        pass

    @abstractmethod
    def validate_source(self, source: str) -> bool:
        pass

