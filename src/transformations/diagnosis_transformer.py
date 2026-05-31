from typing import Dict, Any, List, Iterator
from src.interfaces.transformer_interface import DataTransformer


class DiagnosisTransformer(DataTransformer):
    """Transforme les données des diagnostics"""

    def transform(
        self, data: Iterator[List[Dict[str, Any]]]
    ) -> Iterator[List[Dict[str, Any]]]:
        """Transforme les données brutes des diagnostics"""
        for chunk in data:
            transformed_chunk = []
            for record in chunk:
                cleaned_record = self.clean(record)
                if self.validate(cleaned_record):
                    transformed_record = self._transform_record(cleaned_record)
                    if transformed_record:
                        transformed_chunk.append(transformed_record)
            if transformed_chunk:
                yield transformed_chunk

    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transforme un enregistrement de diagnostic"""
        try:
            transformed = {
                "diagnosis_id": str(
                    record.get("diagnosis_id", record.get("id", ""))
                ).strip(),
                "encounter_id": str(record.get("encounter_id", "")).strip(),
                "provider_id": str(record.get("provider_id", "")).strip(),
                "diagnosis_code": str(record.get("diagnosis_code", "")).strip(),
                "diagnosis_description": str(
                    record.get("diagnosis_description", "")
                ).strip(),
                "diagnosis_date": str(record.get("diagnosis_date", "")),
                "severity": str(record.get("severity", "")),
                "status": str(record.get("status", "active")),
            }
            return transformed
        except Exception as e:
            print(f"Error transforming diagnosis record: {e}")
            return None

    def validate(self, record: Dict[str, Any]) -> bool:
        """Valide un enregistrement de diagnostic"""
        required_fields = ["diagnosis_id", "encounter_id"]
        for field in required_fields:
            if field not in record or not record[field]:
                return False
        return True

    def clean(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie un enregistrement de diagnostic"""
        cleaned = {}
        for key, value in record.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
                if cleaned[key] == "":
                    cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned
