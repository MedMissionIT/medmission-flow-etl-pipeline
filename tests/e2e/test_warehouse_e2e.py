import pandas as pd

from src.warehouse.core.pipeline import WarehousePipeline
from src.warehouse.core.context import WarehouseContext


# -------------------------------------------------------
# FIXTURE LOADER HELPERS
# -------------------------------------------------------

def load_fixture(name: str):
    return pd.read_csv(f"tests/fixtures/{name}.csv")


def build_context():
    """
    Centralise la construction du context
    pour tous les tests d'intégration.
    """

    return WarehouseContext(

        patients=load_fixture("patients"),

        providers=load_fixture("providers"),

        visits=load_fixture("visits"),

        diagnoses=load_fixture("diagnoses"),

        encounters=load_fixture("encounters"),

        prescriptions=load_fixture("prescriptions"),
    )


# -------------------------------------------------------
# PIPELINE SMOKE TEST
# -------------------------------------------------------

def test_pipeline_runs_end_to_end():

    context = build_context()

    result = WarehousePipeline().run(context)

    assert result is not None


# -------------------------------------------------------
# FACT VISIT TESTS (STAR SCHEMA CORE)
# -------------------------------------------------------

def test_fact_visit_exists():

    context = build_context()

    result = WarehousePipeline().run(context)

    assert "fact_visit" in result.facts
    assert len(result.facts["fact_visit"]) > 0


def test_fact_visit_schema():

    context = build_context()

    result = WarehousePipeline().run(context)

    fact = result.facts["fact_visit"]

    expected_columns = [
        "visit_id",
        "patient_key",
        "provider_key",
        "date_key",
        "visit_duration_days"
    ]

    for col in expected_columns:
        assert col in fact.columns


def test_fact_visit_keys_valid():

    context = build_context()

    result = WarehousePipeline().run(context)

    fact = result.facts["fact_visit"]

    assert fact["patient_key"].isnull().sum() == 0
    assert fact["provider_key"].isnull().sum() == 0
    assert fact["date_key"].isnull().sum() == 0


# -------------------------------------------------------
# DIMENSION TESTS
# -------------------------------------------------------

def test_dim_patient_exists():

    context = build_context()

    result = WarehousePipeline().run(context)

    assert "dim_patient" in result.dimensions
    assert len(result.dimensions["dim_patient"]) > 0


def test_dim_provider_exists():

    context = build_context()

    result = WarehousePipeline().run(context)

    assert "dim_provider" in result.dimensions
    assert len(result.dimensions["dim_provider"]) > 0


def test_dim_date_exists():

    context = build_context()

    result = WarehousePipeline().run(context)

    assert "dim_date" in result.dimensions

    dim_date = result.dimensions["dim_date"]

    assert "date_key" in dim_date.columns
    assert len(dim_date) > 0


# -------------------------------------------------------
# DATA QUALITY CHECK (GLOBAL SAFETY NET)
# -------------------------------------------------------

def test_no_null_keys_in_facts():

    context = build_context()

    result = WarehousePipeline().run(context)

    fact = result.facts["fact_visit"]

    critical_keys = [
        "patient_key",
        "provider_key",
        "date_key"
    ]

    for key in critical_keys:
        assert fact[key].isnull().sum() == 0


# -------------------------------------------------------
# INTEGRATION CONSISTENCY CHECK
# -------------------------------------------------------

def test_star_schema_consistency():

    context = build_context()

    result = WarehousePipeline().run(context)

    fact = result.facts["fact_visit"]
    dim_patient = result.dimensions["dim_patient"]

    # patient_key must exist in dimension
    assert fact["patient_key"].isin(
        dim_patient["patient_key"]
    ).all()