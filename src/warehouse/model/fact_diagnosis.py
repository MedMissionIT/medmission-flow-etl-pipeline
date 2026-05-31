import pandas as pd


class FactDiagnosis:

    def build(self, stg_diagnoses, dim_patient, dim_date):

        # ---------------------------------
        # Empty input
        # ---------------------------------

        if stg_diagnoses is None or len(stg_diagnoses) == 0:
            return pd.DataFrame(
                columns=[
                    "diagnosis_id",
                    "patient_key",
                    "date_key",
                    "diagnosis_code"
                ]
            )

        df = stg_diagnoses.copy()

        # ---------------------------------
        # Required columns
        # ---------------------------------

        if "patient_id" not in df.columns:
            raise ValueError(
                f"patient_id missing in diagnoses. Available: {df.columns.tolist()}"
            )

        # ---------------------------------
        # Normalize IDs
        # ---------------------------------

        df["patient_id"] = (
            df["patient_id"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        dim_patient = dim_patient.copy()

        dim_patient["patient_id"] = (
            dim_patient["patient_id"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        # ---------------------------------
        # Surrogate key
        # ---------------------------------

        df["diagnosis_id"] = range(
            1,
            len(df) + 1
        )

        # ---------------------------------
        # Join Patient Dimension
        # ---------------------------------

        df = df.merge(
            dim_patient[
                ["patient_id", "patient_key"]
            ],
            on="patient_id",
            how="left"
        )

        # ---------------------------------
        # Validate patient mapping
        # ---------------------------------

        missing_patients = df["patient_key"].isna().sum()

        if missing_patients > 0:
            raise ValueError(
                f"{missing_patients} diagnoses could not be mapped to dim_patient"
            )

        # ---------------------------------
        # Date Key
        # ---------------------------------

        if "diagnosis_date" in df.columns:

            diagnosis_date = pd.to_datetime(
                df["diagnosis_date"],
                errors="coerce"
            )

            df["date_key"] = (
                diagnosis_date
                .dt.strftime("%Y%m%d")
                .fillna("0")
                .astype(int)
            )

        else:

            # Dataset has no diagnosis date
            df["date_key"] = 0

        # ---------------------------------
        # Diagnosis Code
        # ---------------------------------

        if "diagnosis_code" in df.columns:

            pass

        elif "code" in df.columns:

            df["diagnosis_code"] = df["code"]

        elif "name" in df.columns:

            # OpenMRS export
            df["diagnosis_code"] = df["name"]

        else:

            df["diagnosis_code"] = "UNKNOWN"

        # ---------------------------------
        # Final Fact
        # ---------------------------------

        fact = df[
            [
                "diagnosis_id",
                "patient_key",
                "date_key",
                "diagnosis_code"
            ]
        ].copy()

        return fact