import logging


class ValidationRules:

    @staticmethod
    def check_visits_schema(stg_visits, strict=True):

        if stg_visits is None:

            msg = "stg_visits is missing"

            if strict:
                raise ValueError(msg)
            else:
                logging.warning(msg)
                return

        required_columns = [
            "visit_id",
            "patient_id",
            "visit_date"
        ]

        missing = [
            c for c in required_columns
            if c not in stg_visits.columns
        ]

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        if stg_visits["visit_date"].dtype == "object":
            raise ValueError(
                "visit_date not normalized"
            )