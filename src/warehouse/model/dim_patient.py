import pandas as pd


class DimPatient:

    def build(self, patients):

        if patients is None:
            raise ValueError("patients is None")

        if "patient_id" not in patients.columns:
            raise ValueError("patient_id missing in patients")

        dim = patients.copy()

        # SURROGATE KEY
        dim["patient_key"] = range(1, len(dim) + 1)

        # CLEAN STAR SCHEMA OUTPUT
        return dim[[
            "patient_id",
            "patient_key",
            "gender",
            "birthdate",
            "city_village"
        ]] if set(["gender", "birthdate", "city_village"]).issubset(dim.columns) else dim[[
            "patient_id",
            "patient_key"
        ]]