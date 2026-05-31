from src.warehouse.model.fact_visit import FactVisit
from src.warehouse.model.fact_diagnosis import FactDiagnosis
from src.warehouse.model.fact_prescription import FactPrescription


class FactBuilder:

    def build(self, context):

        context.facts = {}

        # VISIT FACT
        context.facts["fact_visit"] = FactVisit().build(
            context.stg_visits,
            context.dimensions["dim_patient"],
            context.dimensions["dim_provider"],
            context.dimensions["dim_date"]
        )

        # DIAGNOSIS FACT
        context.facts["fact_diagnosis"] = FactDiagnosis().build(
            context.stg_diagnoses,
            context.dimensions["dim_patient"],
            context.dimensions["dim_date"]
        )

        # PRESCRIPTION FACT
        context.facts["fact_prescription"] = FactPrescription().build(
            context.stg_prescriptions,
            context.dimensions["dim_patient"],
            context.dimensions["dim_date"]
        )

        return context