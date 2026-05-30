import logging
from src.infrastructure.csv_reader import CSVReader
from src.infrastructure.csv_writer import CSVWriter
from src.transformations.patient_transformer import PatientTransformer
from src.transformations.encounter_transformer import EncounterTransformer
from src.pipeline.data_pipeline import DataPipeline
from src.pipeline.steps import (
    LoadPatientsStep,
    JoinEncountersStep,
    ProcessDiagnosisStep,
    ProcessPrescriptionsStep,
    ProcessProvidersStep
)
from src.config.logger_config import setup_logging

def main():
    # Configuration
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Initialisation des composants
    reader = CSVReader(chunksize=5000)
    writer = CSVWriter()
    
    transformers = {
        'patient': PatientTransformer(),
        'encounter': EncounterTransformer(),
        'diagnosis': DiagnosisTransformer(),
        'prescription': PrescriptionTransformer(),
        'provider': ProviderTransformer()
    }
    
    # Définition des étapes du pipeline
    steps = [
        LoadPatientsStep(),
        JoinEncountersStep(),
        ProcessDiagnosisStep(),
        ProcessPrescriptionsStep(),
        ProcessProvidersStep()
    ]
    
    # Sources de données
    sources = {
        'patients': "data/input/PATIENT_MASTER.csv",
        'encounters': "data/input/ENCOUNTERS_FACT.csv",
        'diagnosis': "data/input/DIAGNOSIS_FACT.csv",
        'prescriptions': "data/input/PRESCRIPTION_FACT.csv",
        'providers': "data/input/PROVIDER_FACT.csv"
    }
    
    # Création et exécution du pipeline
    pipeline = DataPipeline(reader, writer, transformers, steps)
    
    try:
        result = pipeline.execute(sources, "data/output/")
        logger.info("Pipeline exécuté avec succès")
        
        # Rapports finaux
        generate_report(result)
        
    except Exception as e:
        logger.error(f"Erreur dans le pipeline: {e}")
        raise

def generate_report(result):
    """Génère un rapport sur l'exécution du pipeline"""
    print("=== RAPPORT D'EXÉCUTION ===")
    for key, value in result.items():
        print(f"{key}: {len(value) if hasattr(value, '__len__') else value} éléments")

if __name__ == "__main__":
    main()