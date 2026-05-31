from dataclasses import dataclass
import pandas as pd


@dataclass
class WarehouseContext:

    # RAW

    patients: pd.DataFrame = None

    providers: pd.DataFrame = None

    visits: pd.DataFrame = None

    diagnoses: pd.DataFrame = None

    encounters: pd.DataFrame = None

    prescriptions: pd.DataFrame = None

    # STAGING

    stg_patients: pd.DataFrame = None

    stg_providers: pd.DataFrame = None

    stg_visits: pd.DataFrame = None

    stg_diagnoses: pd.DataFrame = None

    stg_encounters: pd.DataFrame = None

    stg_prescriptions: pd.DataFrame = None

    # DW

    dimensions: dict = None

    facts: dict = None

