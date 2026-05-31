from dataclasses import dataclass


@dataclass
class WarehouseConfig:
    input_path: str = "data/input"
    output_path: str = "data/output"
    date_format: str = "%Y-%m-%d"
    export_csv: bool = True
    export_database: bool = True
    source_systems: list = None
