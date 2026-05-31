import pandas as pd


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

        s = series.astype(str)

        for fr, en in self.MONTH_MAP.items():
            s = s.str.replace(fr, en, regex=False)

        return pd.to_datetime(s, errors="coerce")

    def build(self, context):

        # PATIENTS
        context.stg_patients = (
            context.patients.copy()
            if context.patients is not None
            else None
        )

        # PROVIDERS
        context.stg_providers = (
            context.providers.copy()
            if context.providers is not None
            else None
        )

        # VISITS (IMPORTANT FIX ICI)
        if context.visits is not None:

            stg_visits = context.visits.rename(
                columns={
                    "date_started": "visit_date",
                    "date_stopped": "visit_end_date"
                }
            ).copy()

            stg_visits["visit_date"] = self._normalize_datetime(
                stg_visits["visit_date"]
            )

            stg_visits["visit_end_date"] = self._normalize_datetime(
                stg_visits["visit_end_date"]
            )

            context.stg_visits = stg_visits

        else:
            context.stg_visits = None

        # DIAGNOSES
        context.stg_diagnoses = (
            context.diagnoses.copy()
            if context.diagnoses is not None
            else None
        )

        # ENCOUNTERS
        context.stg_encounters = (
            context.encounters.copy()
            if context.encounters is not None
            else None
        )

        # PRESCRIPTIONS
        context.stg_prescriptions = (
            context.prescriptions.copy()
            if context.prescriptions is not None
            else None
        )

        return context