from src.warehouse.layers.staging_builder import (
    StagingBuilder
)

from src.warehouse.layers.dim_builder import (
    DimensionBuilder
)

from src.warehouse.layers.fact_builder import (
    FactBuilder
)

from src.warehouse.quality.validation_rules import (
    ValidationRules
)


class WarehousePipeline:

    def run(self, context):
        
        context = (
            StagingBuilder()
            .build(context)
        )
        
        ValidationRules.check_visits_schema(
            context.stg_visits
        )

        
        context = (
            DimensionBuilder()
            .build(context)
        )

        context = (
            FactBuilder()
            .build(context)
        )

        return context