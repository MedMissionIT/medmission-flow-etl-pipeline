from src.warehouse.model.dim_patient import DimPatient
from src.warehouse.model.dim_provider import DimProvider
from src.warehouse.model.dim_date import DimDate


class DimensionBuilder:

    def build(self, context):

        context.dimensions = {

            "dim_patient":
                DimPatient().build(
                    context.stg_patients
                ),

            "dim_provider":
                DimProvider().build(
                    context.stg_providers
                ),

            "dim_date":
                DimDate().build(
                    context.stg_visits["visit_date"]
                )
        }

        return context