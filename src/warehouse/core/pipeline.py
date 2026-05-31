from src.warehouse.layers.staging_builder import StagingBuilder
from src.warehouse.layers.dim_builder import DimensionBuilder
from src.warehouse.layers.fact_builder import FactBuilder
from src.warehouse.quality.validation_rules import ValidationRules


class WarehousePipeline:

    def run(self, context):

        # 1. STAGING
        context = StagingBuilder().build(context)

        # 2. VALIDATION GATE
        ValidationRules.check_visits_schema(context.stg_visits)

        # 3. DIMENSIONS
        context = DimensionBuilder().build(context)

        # 4. FACTS
        context = FactBuilder().build(context)

        return context