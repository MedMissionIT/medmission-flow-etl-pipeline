from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os


class PipelineStep(ABC):
    """Classe abstraite pour une étape du pipeline"""

    @abstractmethod
    def execute(self, reader, writer, transformers, sources, context, output_path):
        """
        Exécute une étape du pipeline

        Args:
            reader: Lecteur de données
            writer: Écrivain de données
            transformers: Dictionnaire des transformateurs
            sources: Dictionnaire des sources
            context: Contexte d'exécution
            output_path: Chemin de sortie

        Returns:
            Contexte mis à jour
        """
        pass


class LoadPatientsStep(PipelineStep):
    """Étape 1: Chargement des patients"""

    def execute(self, reader, writer, transformers, sources, context, output_path):
        print("  - Chargement des patients...")

        # Lire les données
        patients_data = []
        try:
            for record in reader.read(sources.get("patients", "")):
                patients_data.append(record)
            print(f"    ✓ {len(patients_data)} patients chargés")
        except Exception as e:
            print(f"    ✗ Erreur chargement patients: {e}")
            patients_data = []

        # Sauvegarder si writer existe
        if writer and patients_data:
            try:
                output_file = os.path.join(output_path, "patients_processed.csv")
                writer.write(patients_data, output_file)
                context["patients_file"] = output_file
            except Exception as e:
                print(f"    ⚠ Sauvegarde patients: {e}")

        # Mettre à jour le contexte
        context["patients"] = patients_data

        return context


class JoinEncountersStep(PipelineStep):
    """Étape 2: Jointure des rencontres"""

    def execute(self, reader, writer, transformers, sources, context, output_path):
        print("  - Traitement des rencontres...")

        # Lire les données
        encounters_data = []
        try:
            for record in reader.read(sources.get("encounters", "")):
                encounters_data.append(record)
            print(f"    ✓ {len(encounters_data)} rencontres chargées")
        except Exception as e:
            print(f"    ✗ Erreur chargement rencontres: {e}")
            encounters_data = []

        # Joindre avec les patients si disponibles
        patients = context.get("patients", [])
        if patients and encounters_data:
            patient_dict = {
                p.get("patient_id"): p for p in patients if p.get("patient_id")
            }

            enriched_encounters = []
            for encounter in encounters_data:
                patient_id = encounter.get("patient_id")
                if patient_id in patient_dict:
                    encounter["patient_name"] = patient_dict[patient_id].get("name", "")
                    encounter["patient_gender"] = patient_dict[patient_id].get(
                        "gender", ""
                    )
                    enriched_encounters.append(encounter)

            encounters_data = enriched_encounters
            print(f"    ✓ {len(encounters_data)} rencontres enrichies")

        # Sauvegarder
        if writer and encounters_data:
            try:
                output_file = os.path.join(output_path, "encounters_enriched.csv")
                writer.write(encounters_data, output_file)
                context["encounters_file"] = output_file
            except Exception as e:
                print(f"    ⚠ Sauvegarde rencontres: {e}")

        context["encounters"] = encounters_data
        return context


class ProcessDiagnosisStep(PipelineStep):
    """Étape 3: Traitement des diagnostics"""

    def execute(self, reader, writer, transformers, sources, context, output_path):
        print("  - Traitement des diagnostics...")

        # Lire les données
        diagnoses_data = []
        try:
            for record in reader.read(sources.get("diagnosis", "")):
                diagnoses_data.append(record)
            print(f"    ✓ {len(diagnoses_data)} diagnostics chargés")
        except Exception as e:
            print(f"    ✗ Erreur chargement diagnostics: {e}")
            diagnoses_data = []

        # Lier avec les rencontres
        encounters = context.get("encounters", [])
        if encounters and diagnoses_data:
            encounter_dict = {
                e.get("encounter_id"): e for e in encounters if e.get("encounter_id")
            }

            linked_diagnoses = []
            for diagnosis in diagnoses_data:
                encounter_id = diagnosis.get("encounter_id")
                if encounter_id in encounter_dict:
                    diagnosis["encounter_date"] = encounter_dict[encounter_id].get(
                        "encounter_date", ""
                    )
                    linked_diagnoses.append(diagnosis)

            diagnoses_data = linked_diagnoses
            print(f"    ✓ {len(diagnoses_data)} diagnostics liés aux rencontres")

        # Sauvegarder
        if writer and diagnoses_data:
            try:
                output_file = os.path.join(output_path, "diagnoses_linked.csv")
                writer.write(diagnoses_data, output_file)
                context["diagnoses_file"] = output_file
            except Exception as e:
                print(f"    ⚠ Sauvegarde diagnostics: {e}")

        context["diagnoses"] = diagnoses_data
        return context


class ProcessPrescriptionsStep(PipelineStep):
    """Étape 4: Traitement des prescriptions"""

    def execute(self, reader, writer, transformers, sources, context, output_path):
        print("  - Traitement des prescriptions...")

        # Lire les données
        prescriptions_data = []
        try:
            # Vérifier la clé correcte pour les prescriptions
            prescriptions_source = sources.get(
                "prescriptions", sources.get("prescription", "")
            )
            for record in reader.read(prescriptions_source):
                prescriptions_data.append(record)
            print(f"    ✓ {len(prescriptions_data)} prescriptions chargées")
        except Exception as e:
            print(f"    ✗ Erreur chargement prescriptions: {e}")
            prescriptions_data = []

        # Lier avec les rencontres si possible
        encounters = context.get("encounters", [])
        if encounters and prescriptions_data:
            encounter_dict = {
                e.get("encounter_id"): e for e in encounters if e.get("encounter_id")
            }

            linked_prescriptions = []
            for prescription in prescriptions_data:
                encounter_id = prescription.get("encounter_id")
                if encounter_id in encounter_dict:
                    prescription["encounter_date"] = encounter_dict[encounter_id].get(
                        "encounter_date", ""
                    )
                    linked_prescriptions.append(prescription)

            prescriptions_data = linked_prescriptions
            print(f"    ✓ {len(prescriptions_data)} prescriptions liées aux rencontres")

        # Sauvegarder
        if writer and prescriptions_data:
            try:
                output_file = os.path.join(output_path, "prescriptions_processed.csv")
                writer.write(prescriptions_data, output_file)
                context["prescriptions_file"] = output_file
            except Exception as e:
                print(f"    ⚠ Sauvegarde prescriptions: {e}")

        context["prescriptions"] = prescriptions_data
        return context


class ProcessProvidersStep(PipelineStep):
    """Étape 5: Traitement des fournisseurs"""

    def execute(self, reader, writer, transformers, sources, context, output_path):
        print("  - Traitement des fournisseurs...")

        # Lire les données
        providers_data = []
        try:
            for record in reader.read(sources.get("providers", "")):
                providers_data.append(record)
            print(f"    ✓ {len(providers_data)} fournisseurs chargés")
        except Exception as e:
            print(f"    ✗ Erreur chargement fournisseurs: {e}")
            providers_data = []

        # Lier avec les diagnostics si disponible
        diagnoses = context.get("diagnoses", [])
        if diagnoses and providers_data:
            provider_ids = set(
                p.get("provider_id") for p in providers_data if p.get("provider_id")
            )
            linked_count = sum(
                1 for d in diagnoses if d.get("provider_id") in provider_ids
            )
            print(f"    ✓ {linked_count} diagnostics liés aux fournisseurs")

        # Sauvegarder
        if writer and providers_data:
            try:
                output_file = os.path.join(output_path, "providers_processed.csv")
                writer.write(providers_data, output_file)
                context["providers_file"] = output_file
            except Exception as e:
                print(f"    ⚠ Sauvegarde fournisseurs: {e}")

        context["providers"] = providers_data
        return context
