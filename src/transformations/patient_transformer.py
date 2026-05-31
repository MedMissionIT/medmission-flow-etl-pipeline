from typing import Dict, Any, List, Iterator
from src.interfaces.transformer_interface import DataTransformer


class PatientTransformer(DataTransformer):
    """Transforme les données des patients"""

    def transform(
        self, data: Iterator[List[Dict[str, Any]]]
    ) -> Iterator[List[Dict[str, Any]]]:
        """Transforme les données brutes des patients"""
        for chunk in data:
            transformed_chunk = []
            for record in chunk:
                # Nettoyer d'abord
                cleaned_record = self.clean(record)
                # Valider ensuite
                if self.validate(cleaned_record):
                    transformed_record = self._transform_record(cleaned_record)
                    if transformed_record:
                        transformed_chunk.append(transformed_record)
            if transformed_chunk:
                yield transformed_chunk

    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transforme un enregistrement patient individuel"""
        try:
            transformed = {
                "patient_id": str(record.get("patient_id", "")).strip(),
                "name": str(record.get("name", "")).strip(),
                "birth_date": str(record.get("birth_date", "")),
                "gender": str(record.get("gender", "")).upper(),
                "address": str(record.get("address", "")),
                "phone": str(record.get("phone", "")),
                "email": str(record.get("email", "")),
            }
            return transformed
        except Exception as e:
            print(f"Error transforming patient record: {e}")
            return None

    def validate(self, record: Dict[str, Any]) -> bool:
        """Valide un enregistrement patient"""
        # Vérifier les champs obligatoires
        required_fields = ["patient_id", "name"]
        for field in required_fields:
            if field not in record or not record[field]:
                return False

        # Vérifier que patient_id n'est pas vide
        if not str(record.get("patient_id", "")).strip():
            return False

        return True

    def clean(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie un enregistrement patient"""
        cleaned = {}
        for key, value in record.items():
            if isinstance(value, str):
                # Supprimer les espaces inutiles
                cleaned[key] = value.strip()
                # Convertir les chaînes vides en None
                if cleaned[key] == "":
                    cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned
