from abc import ABC, abstractmethod
from typing import Dict, Any


class PipelineStep(ABC):
    @abstractmethod
    def execute(self, reader, writer, transformers, sources, context):
        pass


class LoadPatientsStep(PipelineStep):
    def execute(self, reader, writer, transformers, sources, context):
        patients_data = reader.read(sources["patients"])
        transformed_data = transformers["patient"].transform(patients_data)

        # Validation et transformation
        validated_data = self._validate(transformed_data)

        # Sauvegarde intermédiaire
        writer.write(validated_data, "output/patients_processed.csv")

        context["patients"] = validated_data
        return context

    def _validate(self, data):
        # Logique de validation
        return data


class JoinEncountersStep(PipelineStep):
    def execute(self, reader, writer, transformers, sources, context):
        encounters = reader.read(sources["encounters"])
        patients = context.get("patients", [])

        joined_data = transformers["encounter"].join_with_patients(encounters, patients)

        context["encounters"] = joined_data
        return context


class ProcessDiagnosisStep(PipelineStep):
    def execute(self, reader, writer, transformers, sources, context):
        diagnoses = reader.read(sources["diagnosis"])
        encounters = context.get("encounters", [])

        linked_diagnoses = transformers["diagnosis"].link_to_encounters(
            diagnoses, encounters
        )

        context["diagnoses"] = linked_diagnoses
        return context
