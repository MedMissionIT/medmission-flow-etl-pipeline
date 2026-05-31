class CrossSourceMatcher:

    def match_patients(self, openmrs, ophtalmo):
        openmrs["patient_key"] = openmrs["patient_id"].astype(str)
        ophtalmo["patient_key"] = (
            ophtalmo["nom"].str.upper()
            + "_"
            + ophtalmo["prenom"].str.upper()
            + "_"
            + ophtalmo["date_naissance"].astype(str)
        )

        return openmrs, ophtalmo
