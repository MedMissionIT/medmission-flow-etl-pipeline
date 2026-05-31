import pandas as pd

class FactVisit:
    def build(self, stg_visits, dim_patient, dim_provider, dim_date):
        if stg_visits is None:
            raise ValueError("stg_visits is None")

        df = stg_visits.copy()

        # ----------------------------
        # RENOMMAGE (Adaptation aux données réelles)
        # ----------------------------
        # Tes données CSV utilisent 'date_started', le code attend 'visit_date'
        if "date_started" in df.columns and "visit_date" not in df.columns:
            df = df.rename(columns={"date_started": "visit_date", "date_stopped": "visit_end_date"})

        # ----------------------------
        # PATIENT KEY
        # ----------------------------
        if "patient_id" not in df.columns:
            raise ValueError("patient_id missing in stg_visits")

        # Conversion en numérique pour assurer la jointure
        df['patient_id'] = pd.to_numeric(df['patient_id'], errors='coerce')
        dim_patient_local = dim_patient.copy()
        dim_patient_local['patient_id'] = pd.to_numeric(dim_patient_local['patient_id'], errors='coerce')

        df = df.merge(
            dim_patient_local[["patient_id", "patient_key"]],
            on="patient_id",
            how="left"
        )

        # ----------------------------
        # PROVIDER KEY (Fix des 2455 NULLs)
        # ----------------------------
        # Si provider_id est absent du CSV, on le simule ou on le gère proprement
        if "provider_id" not in df.columns:
            # Si tes données n'ont pas de provider, on met une clé par défaut (ex: 0)
            df["provider_key"] = 0 
        elif dim_provider is not None:
            # Force le type string pour éviter les échecs de jointure (101 vs "101")
            df['provider_id'] = df['provider_id'].astype(str)
            dim_provider_local = dim_provider.copy()
            dim_provider_local['provider_id'] = dim_provider_local['provider_id'].astype(str)

            df = df.merge(
                dim_provider_local[["provider_id", "provider_key"]],
                on="provider_id",
                how="left"
            )
        else:
            df["provider_key"] = None

        # ----------------------------
        # DATE KEY
        # ----------------------------
        if "visit_date" not in df.columns:
            raise ValueError("visit_date (or date_started) missing in stg_visits")

        # Transformation de la date "mai 13, 2022..." en clé numérique YYYYMMDD
        # Note: dayfirst=False car le format semble être Mois Jour, Année
        visit_dates = pd.to_datetime(df["visit_date"], errors="coerce")
        df["date_key"] = (
            visit_dates.dt.strftime("%Y%m%d")
            .fillna(0) # Sécurité pour les lignes vides
            .astype(int) 
        )

        # ----------------------------
        # MEASURES (Durée du séjour)
        # ----------------------------
        if "visit_end_date" in df.columns:
            end_dates = pd.to_datetime(df["visit_end_date"], errors="coerce")
            df["visit_duration_days"] = (end_dates - visit_dates).dt.days
        else:
            df["visit_duration_days"] = 0

        # ----------------------------
        # FINAL FACT TABLE
        # ----------------------------
        # On s'assure que location_id existe pour ne pas faire planter le filtre final
        if "location_id" not in df.columns:
            df["location_id"] = None

        return df[[
            "visit_id",
            "patient_key",
            "provider_key",
            "date_key",
            "visit_duration_days"
        ]].copy()