from typing import List, Dict, Any
from src.interfaces.reader_interface import DataReader
from src.interfaces.writer_interface import DataWriter
from src.interfaces.transformer_interface import DataTransformer
from src.pipeline.base_pipeline import BasePipeline
from src.pipeline.steps import PipelineStep


class DataPipeline(BasePipeline):
    def __init__(
        self,
        reader: DataReader,
        writer: DataWriter,
        transformers: Dict[str, DataTransformer],
        steps: List[PipelineStep],
    ):
        self.reader = reader
        self.writer = writer
        self.transformers = transformers
        self.steps = steps

    def execute(self, sources: Dict[str, str], output_path: str):
        context = {}

        for step in self.steps:
            context = step.execute(
                reader=self.reader,
                writer=self.writer,
                transformers=self.transformers,
                sources=sources,
                context=context,
            )

        return context
