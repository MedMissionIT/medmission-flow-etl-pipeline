from warehouse.layers.raw_loader import RawLoader
from warehouse.layers.staging_builder import StagingBuilder
from warehouse.models.fact_medmission import FactMedMission
from warehouse.models.fact_ophtalmo import FactOphtalmo
from warehouse.exporters.csv_exporter import CSVExporter


class WarehouseBuilder:

    def __init__(self, config):
        self.config = config
        self.raw_loader = RawLoader(config)
        self.staging = StagingBuilder()
        self.exporter = CSVExporter()

    def load_raw(self):
        self.openmrs = self.raw_loader.load_openmrs()
        self.ophtalmo = self.raw_loader.load_ophtalmo()

    def build_staging(self):
        self.stg_patients = self.staging.normalize_patients(self.openmrs["patients"])

    def build_dimensions(self):
        pass  # étape suivante

    def build_facts(self):
        self.fact_ophtalmo = FactOphtalmo().build(
            self.ophtalmo["screening"], self.ophtalmo["surgery"]
        )

    def build_marts(self):
        self.exporter.export(self.fact_ophtalmo, "FACT_OPHTALMO")
from abc import ABC, abstractmethod


class Builder(ABC):

    @abstractmethod
    def build(self, context):
        pass