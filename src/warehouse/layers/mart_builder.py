# src/warehouse/layers/mart_builder.py (extension)
from src.warehouse.integration import CrossSourceMatcher, OphtalmoMapper
from src.warehouse.model.dim_patient import DimPatient


class MartBuilder:
    def build_master_patient_index(self, context) -> pd.DataFrame:
        """Construit l'index maître des patients"""
        
        # 1. Charger les patients OpenMRS
        openmrs_patients = context.dimensions.get('dim_patient')
        if openmrs_patients is None:
            # Ou charger depuis staging
            openmrs_patients = context.stg_patients
        
        # 2. Charger les données ophtalmologie
        ophtalmo_mapper = OphtalmoMapper()
        
        # Charger les screenings
        screening_df = pd.read_csv('data/output/FACT_OPHTALMO_SCREENING.csv')
        surgery_df = pd.read_csv('data/output/FACT_OPHTALMO_SURGERY.csv')
        
        # Extraire les patients uniques des données ophtalmologie
        ophtalmo_patients = self._extract_unique_patients(screening_df, surgery_df)
        ophtalmo_patients = ophtalmo_mapper.map_to_standard_format(ophtalmo_patients)
        
        # 3. Match cross-source
        matcher = CrossSourceMatcher(threshold_high=0.85, threshold_medium=0.65)
        matched_patients = matcher.match_patients(
            openmrs_patients,
            ophtalmo_patients,
            source_name="ophtalmo"
        )
        
        # 4. Convertir en DataFrame
        mpi_df = pd.DataFrame([p.to_dict() for p in matched_patients])
        
        # 5. Sauvegarder dans le contexte
        context.dimensions['master_patient_index'] = mpi_df
        
        return mpi_df
    
    def _extract_unique_patients(self, screening_df: pd.DataFrame, surgery_df: pd.DataFrame) -> pd.DataFrame:
        """Extrait les patients uniques des données ophtalmologie"""
        patients = []
        
        for df in [screening_df, surgery_df]:
            if df is not None and not df.empty:
                # Colonnes patient typiques dans ophtalmologie
                patient_cols = [col for col in df.columns if 'patient' in col.lower() or 'nom' in col.lower()]
                
                if patient_cols:
                    # Prendre la première colonne patient trouvée
                    patient_col = patient_cols[0]
                    patients_df = df[[patient_col]].drop_duplicates()
                    patients_df.columns = ['patient_id']
                    patients.append(patients_df)
        
        if patients:
            return pd.concat(patients, ignore_index=True).drop_duplicates()
        return pd.DataFrame()