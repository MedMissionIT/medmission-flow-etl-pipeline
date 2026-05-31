class DataWarehouseBuilder:

    def __init__(self, config):
        self.config = config

    def run(self):
        print("1. Load RAW data")
        patients = self.load_raw_patients()
        encounters = self.load_raw_encounters()
        ophtalmo = self.load_raw_ophtalmo()

        print("2. Build STAGING layer")
        stg_patients = self.build_staging_patients(patients)
        stg_encounters = self.build_staging_encounters(encounters)
        stg_ophtalmo = self.build_staging_ophtalmo(ophtalmo)

        print("3. Build DIMENSIONS")
        dim_patient = self.build_dim_patient(stg_patients, stg_ophtalmo)

        print("4. Build FACTS")
        fact_medmission = self.build_fact_medmission(
            stg_encounters, stg_ophtalmo, dim_patient
        )

        print("5. Export MART")
        self.export(fact_medmission, dim_patient)
