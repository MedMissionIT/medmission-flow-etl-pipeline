from pathlib import Path

import pandas as pd

from src.warehouse.core.context import WarehouseContext
from src.warehouse.core.pipeline import WarehousePipeline


FIXTURE_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "fixtures"
)


def test_complete_warehouse():

    context = WarehouseContext(

        patients=pd.read_csv(
            FIXTURE_DIR / "patients.csv"
        ),

        providers=pd.read_csv(
            FIXTURE_DIR / "providers.csv"
        ),

        visits=pd.read_csv(
            FIXTURE_DIR / "visits.csv"
        ),

        diagnoses=pd.read_csv(
            FIXTURE_DIR / "diagnoses.csv"
        ),

        encounters=pd.read_csv(
            FIXTURE_DIR / "encounters.csv"
        ),

        prescriptions=pd.read_csv(
            FIXTURE_DIR / "prescriptions.csv"
        )
    )

    print(context.visits.columns.tolist())
    
    
    result = WarehousePipeline().run(context)

    assert "dim_patient" in result.dimensions

    assert "fact_visit" in result.facts
    
    assert "visit_date" in result.stg_visits.columns

    assert len(result.dimensions["dim_patient"]) > 0
    
    assert "dim_date" in result.dimensions

    