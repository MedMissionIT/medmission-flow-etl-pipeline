import pandas as pd
import re
from dateutil import parser


class StagingBuilder:

    MONTH_MAP = {
        "janvier": "January",
        "février": "February",
        "mars": "March",
        "avril": "April",
        "mai": "May",
        "juin": "June",
        "juillet": "July",
        "août": "August",
        "septembre": "September",
        "octobre": "October",
        "novembre": "November",
        "décembre": "December",
    }

    def _normalize_datetime(self, series):

        def parse_value(x):

            if pd.isna(x):
                return pd.NaT

            s = str(x).strip()

            for fr, en in self.MONTH_MAP.items():
                s = s.replace(fr, en)

            s = re.sub(r"\s+", " ", s)

            try:
                return parser.parse(s)
            except Exception:
                return pd.NaT

        return series.apply(parse_value)

    def _normalize_id(self, series):

        return (
            series.astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

    def build(self, context):

        # ==================================================
        # PATIENTS
        # ==================================================

        if context.patients is not None:

            stg_patients = context.patients.copy()

            if "patient_id" in stg_patients.columns:
                stg_patients["patient_id"] = self._normalize_id(
                    stg_patients["patient_id"]
                )

            context.stg_patients = stg_patients

        else:
            context.stg_patients = None

        # ==================================================
        # PROVIDERS
        # ==================================================

        if context.providers is not None:

            stg_providers = context.providers.copy()

            if "provider_id" not in stg_providers.columns:
                raise ValueError(
                    "providers must contain provider_id"
                )

            stg_providers["provider_id"] = self._normalize_id(
                stg_providers["provider_id"]
            )

            context.stg_providers = stg_providers

        else:
            context.stg_providers = None

        # ==================================================
        # VISITS
        # ==================================================

        if context.visits is not None:

            stg_visits = (
                context.visits
                .rename(
                    columns={
                        "date_started": "visit_date",
                        "date_stopped": "visit_end_date"
                    }
                )
                .copy()
            )

            required_cols = ["visit_id", "patient_id"]

            for col in required_cols:
                if col not in stg_visits.columns:
                    raise ValueError(
                        f"VISITS missing required column: {col}"
                    )

            stg_visits["visit_id"] = self._normalize_id(
                stg_visits["visit_id"]
            )

            stg_visits["patient_id"] = self._normalize_id(
                stg_visits["patient_id"]
            )

            stg_visits["visit_date"] = self._normalize_datetime(
                stg_visits["visit_date"]
            )

            stg_visits["visit_end_date"] = self._normalize_datetime(
                stg_visits["visit_end_date"]
            )

            context.stg_visits = stg_visits

        else:
            context.stg_visits = None

        # ==================================================
        # DIAGNOSES
        # ==================================================

        if context.diagnoses is not None:

            stg_diag = context.diagnoses.copy()

            if (
                "person_id" in stg_diag.columns
                and "patient_id" not in stg_diag.columns
            ):
                stg_diag = stg_diag.rename(
                    columns={
                        "person_id": "patient_id"
                    }
                )

            if "patient_id" in stg_diag.columns:
                stg_diag["patient_id"] = self._normalize_id(
                    stg_diag["patient_id"]
                )

            context.stg_diagnoses = stg_diag

        else:
            context.stg_diagnoses = None

        # ==================================================
        # ENCOUNTERS
        # ==================================================

        if context.encounters is not None:

            stg_enc = context.encounters.copy()

            if "visit_id" in stg_enc.columns:
                stg_enc["visit_id"] = self._normalize_id(
                    stg_enc["visit_id"]
                )

            if "provider_id" in stg_enc.columns:
                stg_enc["provider_id"] = self._normalize_id(
                    stg_enc["provider_id"]
                )

            context.stg_encounters = stg_enc

        else:
            context.stg_encounters = None

        # ==================================================
        # PRESCRIPTIONS
        # ==================================================

        if context.prescriptions is not None:

            stg_presc = context.prescriptions.copy()

            if (
                "person_id" in stg_presc.columns
                and "patient_id" not in stg_presc.columns
            ):
                stg_presc = stg_presc.rename(
                    columns={
                        "person_id": "patient_id"
                    }
                )

            if "patient_id" in stg_presc.columns:
                stg_presc["patient_id"] = self._normalize_id(
                    stg_presc["patient_id"]
                )

            if "date" in stg_presc.columns:
                stg_presc = stg_presc.rename(
                    columns={
                        "date": "prescription_date"
                    }
                )

            elif "created_at" in stg_presc.columns:
                stg_presc = stg_presc.rename(
                    columns={
                        "created_at": "prescription_date"
                    }
                )

            if "prescription_date" in stg_presc.columns:
                stg_presc["prescription_date"] = (
                    self._normalize_datetime(
                        stg_presc["prescription_date"]
                    )
                )

            context.stg_prescriptions = stg_presc

        else:
            context.stg_prescriptions = None

        # ==================================================
        # VISIT -> PROVIDER ENRICHMENT
        # ==================================================

        if (
            context.stg_visits is not None
            and context.stg_encounters is not None
        ):

            enc = context.stg_encounters

            if (
                "visit_id" in enc.columns
                and "provider_id" in enc.columns
            ):

                provider_map = (
                    enc[
                        ["visit_id", "provider_id"]
                    ]
                    .dropna()
                    .drop_duplicates()
                )

                context.stg_visits = (
                    context.stg_visits.merge(
                        provider_map,
                        on="visit_id",
                        how="left"
                    )
                )

        return context