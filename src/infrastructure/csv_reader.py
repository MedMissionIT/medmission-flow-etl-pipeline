import pandas as pd
from typing import Iterator, Dict, Any
from src.interfaces.reader_interface import DataReader


class CSVReader(DataReader):
    def __init__(self, chunksize: int = 10000):
        self.chunksize = chunksize

    def read(self, source: str) -> Iterator[Dict[str, Any]]:
        for chunk in pd.read_csv(source, chunksize=self.chunksize):
            yield chunk.to_dict("records")

    def validate_source(self, source: str) -> bool:
        try:
            pd.read_csv(source, nrows=1)
            return True
        except Exception:
            return False
