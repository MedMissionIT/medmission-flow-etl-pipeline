from typing import Dict, Any, List, Iterator
from src.interfaces.transformer_interface import DataTransformer


class PrescriptionTransformer(DataTransformer):
    """Transforme les données des prescriptions"""

    def transform(
        self, data: Iterator[List[Dict[str, Any]]]
    ) -> Iterator[List[Dict[str, Any]]]:
        """Transforme les données brutes des prescriptions"""
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
        """Transforme un enregistrement de prescription"""
        try:
            transformed = {
                "prescription_id": str(
                    record.get("prescription_id", record.get("id", ""))
                ).strip(),
                "encounter_id": str(record.get("encounter_id", "")).strip(),
                "medication_code": str(record.get("medication_code", "")).strip(),
                "medication_name": str(record.get("medication_name", "")).strip(),
                "dosage": str(record.get("dosage", "")),
                "frequency": str(record.get("frequency", "")),
                "duration": str(record.get("duration", "")),
                "prescribed_date": str(record.get("prescribed_date", "")),
                "refills": int(record.get("refills", 0)),
                "status": str(record.get("status", "active")),
            }
            return transformed
        except Exception as e:
            print(f"Error transforming prescription record: {e}")
            return None

    def validate(self, record: Dict[str, Any]) -> bool:
        """Valide un enregistrement de prescription"""
        required_fields = ["prescription_id", "encounter_id"]
        for field in required_fields:
            if field not in record or not record[field]:
                return False
        return True

    def clean(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie un enregistrement de prescription"""
        cleaned = {}
        for key, value in record.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
                if cleaned[key] == "":
                    cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned
