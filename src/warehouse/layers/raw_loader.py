import pandas as pd


class RawLoader:

    def __init__(self, config):
        self.config = config

    def load_openmrs(self):
        return {
            "patients": pd.read_csv(f"{self.config.input_path}/PATIENT_MASTER.csv"),
            "encounters": pd.read_csv(f"{self.config.input_path}/ENCOUNTERS_FACT.csv"),
            "diagnosis": pd.read_csv(f"{self.config.input_path}/DIAGNOSIS_FACT.csv"),
        }

    def load_ophtalmo(self):
        return {
            "screening": pd.read_csv(
                f"{self.config.input_path}/ophtalmo_vus_clean.csv"
            ),
            "surgery": pd.read_csv(
                f"{self.config.input_path}/ophtalmo_operes_clean.csv"
            ),
        }
