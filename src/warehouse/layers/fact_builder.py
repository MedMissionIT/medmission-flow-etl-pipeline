from src.warehouse.model.fact_visit import FactVisit
from src.warehouse.model.fact_diagnosis import FactDiagnosis


class FactBuilder:

    def build(self, context):

        context.facts = {

            "fact_visit":
                FactVisit().build(
                    context.stg_visits
                ),

            "fact_diagnosis":
                FactDiagnosis().build(
                    context.stg_diagnoses
                )
        }

        return context