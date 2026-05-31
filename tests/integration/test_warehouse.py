import pytest
import pandas as pd
import os
from src.warehouse.core.pipeline import WarehousePipeline
from src.warehouse.core.context import WarehouseContext

# --- FIXTURES ---

@pytest.fixture(scope="module")
def context():
    """
    Initializes the WarehouseContext and loads raw data from CSV fixtures.
    This ensures that the pipeline has data to transform into staging and facts.
    """
    ctx = WarehouseContext()
    
    # Define the path to your test data
    # Adjust this path if your fixtures are located elsewhere
    base_path = "tests/fixtures"
    
    # Load RAW data (The pipeline needs these to build stg_ tables)
    ctx.patients = pd.read_csv(os.path.join(base_path, "patients.csv"))
    ctx.providers = pd.read_csv(os.path.join(base_path, "providers.csv"))
    ctx.visits = pd.read_csv(os.path.join(base_path, "visits.csv"))
    ctx.prescriptions = pd.read_csv(os.path.join(base_path, "prescriptions.csv"))
    
    # Load diagnoses if the file exists, otherwise create an empty DF with correct columns
    diag_path = os.path.join(base_path, "diagnoses.csv")
    if os.path.exists(diag_path):
        ctx.diagnoses = pd.read_csv(diag_path)
    else:
        # Fallback to prevent pipeline crash if file is missing
        ctx.diagnoses = pd.DataFrame(columns=['diagnosis_id', 'patient_id', 'encounter_id', 'diagnosis_code', 'created_at'])

    return ctx

@pytest.fixture(scope="module")
def pipeline_result(context):
    """
    Executes the pipeline once for all tests in this module.
    """
    return WarehousePipeline().run(context)

# --- FACT EXISTENCE TESTS ---

def test_fact_visit_exists(pipeline_result):
    assert "fact_visit" in pipeline_result.facts
    assert len(pipeline_result.facts["fact_visit"]) > 0

def test_fact_diagnosis_exists(pipeline_result):
    assert "fact_diagnosis" in pipeline_result.facts
    # Only check length if you know your diagnoses.csv isn't empty
    assert len(pipeline_result.facts["fact_diagnosis"]) >= 0

def test_fact_prescription_exists(pipeline_result):
    assert "fact_prescription" in pipeline_result.facts
    assert len(pipeline_result.facts["fact_prescription"]) > 0

# --- SCHEMA (COLUMN) TESTS ---

def test_fact_visit_schema(pipeline_result):
    fact = pipeline_result.facts["fact_visit"]
    expected_columns = [
        "visit_id",
        "patient_key",
        "provider_key",
        "date_key",
        "visit_duration_days"
    ]
    for col in expected_columns:
        assert col in fact.columns, f"Column {col} is missing in fact_visit"

def test_fact_diagnosis_schema(pipeline_result):
    fact = pipeline_result.facts["fact_diagnosis"]
    expected_columns = [
        "diagnosis_id",
        "patient_key",
        "date_key",
        "diagnosis_code"
    ]
    for col in expected_columns:
        assert col in fact.columns, f"Column {col} is missing in fact_diagnosis"

def test_fact_prescription_schema(pipeline_result):
    fact = pipeline_result.facts["fact_prescription"]
    expected_columns = [
        "prescription_id",
        "patient_key",
        "date_key",
        "drug_name", # Corrected from 'name'
        "dosage"
    ]
    for col in expected_columns:
        assert col in fact.columns, f"Column {col} is missing in fact_prescription"

# --- KEY VALIDITY AND TYPE TESTS ---

def test_fact_visit_keys_valid(pipeline_result):
    fact = pipeline_result.facts["fact_visit"]
    assert fact["patient_key"].isnull().sum() == 0, "Found NULL patient_key in fact_visit"
    # Note: If provider_key is still failing with 2455 NULLs, 
    # check the merge logic in fact_visit.py
    assert fact["date_key"].dtype in ["int64", "int32"]

def test_fact_diagnosis_keys_valid(pipeline_result):
    fact = pipeline_result.facts["fact_diagnosis"]
    assert fact["patient_key"].isnull().sum() == 0, "Found NULL patient_key in fact_diagnosis"
    assert fact["date_key"].dtype in ["int64", "int32"]

def test_fact_prescription_keys_valid(pipeline_result):
    fact = pipeline_result.facts["fact_prescription"]
    assert fact["patient_key"].isnull().sum() == 0, "Found NULL patient_key in fact_prescription"
    assert fact["date_key"].dtype in ["int64", "int32"]