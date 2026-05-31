import logging
import sys
import os

# Ajouter le chemin du projet au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infrastructure.csv_reader import CSVReader
from src.infrastructure.csv_writer import CSVWriter
from src.transformations.patient_transformer import PatientTransformer
from src.transformations.encounter_transformer import EncounterTransformer
from src.transformations.diagnosis_transformer import DiagnosisTransformer
from src.transformations.prescription_transformer import PrescriptionTransformer
from src.transformations.provider_transformer import ProviderTransformer
from src.pipeline.data_pipeline import DataPipeline
from src.pipeline.steps import (
    LoadPatientsStep,
    JoinEncountersStep,
    ProcessDiagnosisStep,
    ProcessPrescriptionsStep,
    ProcessProvidersStep,
)


def main():
    """Point d'entrée principal du pipeline"""

    print("=" * 60)
    print("MedFlow ETL Pipeline - Traitement des données de santé")
    print("=" * 60)

    # Créer les dossiers nécessaires
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    try:
        # Initialisation des composants
        print("\n1. Initialisation des composants...")
        reader = CSVReader(chunksize=5000)
        writer = CSVWriter()
        print("   ✓ Reader et Writer initialisés")

        transformers = {
            "patient": PatientTransformer(),
            "encounter": EncounterTransformer(),
            "diagnosis": DiagnosisTransformer(),
            "prescription": PrescriptionTransformer(),
            "provider": ProviderTransformer(),
        }
        print("   ✓ Transformateurs initialisés")

        # Définition des étapes du pipeline
        steps = [
            LoadPatientsStep(),
            JoinEncountersStep(),
            ProcessDiagnosisStep(),
            ProcessPrescriptionsStep(),
            ProcessProvidersStep(),
        ]
        print("   ✓ Étapes du pipeline définies")

        # Sources de données
        sources = {
            "patients": "data/input/PATIENT_MASTER.csv",
            "encounters": "data/input/ENCOUNTERS_FACT.csv",
            "diagnosis": "data/input/DIAGNOSIS_FACT.csv",
            "prescriptions": "data/input/PRESCRIPTION_FACT.csv",
            "providers": "data/input/PROVIDER_FACT.csv",
        }

        # Vérifier l'existence des fichiers
        print("\n2. Vérification des fichiers sources...")
        missing_files = []
        for name, path in sources.items():
            if os.path.exists(path):
                print(f"   ✓ {name}: {path}")
            else:
                print(f"   ✗ {name}: {path} (fichier manquant)")
                missing_files.append(name)

        if missing_files:
            print(
                f"\n⚠ Attention: {len(missing_files)} fichier(s) manquant(s): {missing_files}"
            )
            print("   Création de fichiers d'exemple pour tester...")
            create_sample_files(sources)

        # Création et exécution du pipeline
        print("\n3. Exécution du pipeline...")
        pipeline = DataPipeline(reader, writer, transformers, steps)

        result = pipeline.execute(sources, "data/output/")

        # Affichage des résultats
        print("\n" + "=" * 60)
        print("RÉSULTATS DE L'EXÉCUTION")
        print("=" * 60)
        for key, value in result.items():
            if isinstance(value, list):
                print(f"  - {key}: {len(value)} enregistrements")
            elif isinstance(value, str):
                print(f"  - {key}: {value}")
            else:
                print(f"  - {key}: {type(value).__name__}")

        print("\n✅ Pipeline exécuté avec succès!")

    except Exception as e:
        print(f"\n❌ Erreur dans le pipeline: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


def create_sample_files(sources):
    """Crée des fichiers d'exemple pour tester le pipeline"""
    import pandas as pd

    # Créer des données d'exemple
    sample_patients = pd.DataFrame(
        {
            "patient_id": ["P001", "P002", "P003"],
            "name": ["Jean Dupont", "Marie Martin", "Pierre Durand"],
            "birth_date": ["1980-01-01", "1990-02-02", "1975-03-03"],
            "gender": ["M", "F", "M"],
        }
    )

    sample_encounters = pd.DataFrame(
        {
            "encounter_id": ["E001", "E002", "E003"],
            "patient_id": ["P001", "P002", "P001"],
            "encounter_date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "encounter_type": ["Consultation", "Urgence", "Suivi"],
        }
    )

    sample_diagnosis = pd.DataFrame(
        {
            "diagnosis_id": ["D001", "D002", "D003"],
            "encounter_id": ["E001", "E002", "E003"],
            "provider_id": ["PR001", "PR002", "PR001"],
            "diagnosis_code": ["J00", "I10", "E11"],
            "diagnosis_description": ["Rhume", "Hypertension", "Diabète"],
        }
    )

    sample_prescriptions = pd.DataFrame(
        {
            "prescription_id": ["RX001", "RX002", "RX003"],
            "encounter_id": ["E001", "E002", "E003"],
            "medication_code": ["PARA500", "AMLO10", "METF850"],
            "dosage": ["500mg", "10mg", "850mg"],
        }
    )

    sample_providers = pd.DataFrame(
        {
            "provider_id": ["PR001", "PR002", "PR003"],
            "provider_name": ["Dr. Bernard", "Dr. Petit", "Dr. Robert"],
            "specialty": ["Généraliste", "Cardiologue", "Endocrinologue"],
        }
    )

    # Sauvegarder les fichiers
    sample_patients.to_csv(sources["patients"], index=False)
    sample_encounters.to_csv(sources["encounters"], index=False)
    sample_diagnosis.to_csv(sources["diagnosis"], index=False)
    sample_prescriptions.to_csv(sources["prescriptions"], index=False)
    sample_providers.to_csv(sources["providers"], index=False)

    print("   ✓ Fichiers d'exemple créés dans data/input/")


if __name__ == "__main__":
    sys.exit(main())
