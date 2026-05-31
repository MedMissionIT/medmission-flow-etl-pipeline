from typing import Dict, Any, List, Iterator
from src.interfaces.transformer_interface import DataTransformer


class EncounterTransformer(DataTransformer):
    """Transforme les données des rencontres médicales"""

    def transform(
        self, data: Iterator[List[Dict[str, Any]]]
    ) -> Iterator[List[Dict[str, Any]]]:
        """Transforme les données brutes des rencontres"""
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
        """Transforme un enregistrement de rencontre"""
        try:
            transformed = {
                "encounter_id": str(
                    record.get("encounter_id", record.get("id", ""))
                ).strip(),
                "patient_id": str(record.get("patient_id", "")).strip(),
                "encounter_date": str(record.get("encounter_date", "")),
                "encounter_type": str(record.get("encounter_type", "")),
                "department": str(record.get("department", "")),
                "status": str(record.get("status", "completed")),
                "provider_id": str(record.get("provider_id", "")).strip(),
            }
            return transformed
        except Exception as e:
            print(f"Error transforming encounter record: {e}")
            return None

    def validate(self, record: Dict[str, Any]) -> bool:
        """Valide un enregistrement de rencontre"""
        required_fields = ["encounter_id", "patient_id"]
        for field in required_fields:
            if field not in record or not record[field]:
                return False
        return True

    def clean(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie un enregistrement de rencontre"""
        cleaned = {}
        for key, value in record.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
                if cleaned[key] == "":
                    cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned
