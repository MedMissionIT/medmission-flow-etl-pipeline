import pandas as pd


class DimPatient:

    def build(self, patients):

        if patients is None:

            raise ValueError(
                "patients dataframe is None"
            )

        dim = patients.copy()

        dim["patient_key"] = range(
            1,
            len(dim) + 1
        )

        return dim