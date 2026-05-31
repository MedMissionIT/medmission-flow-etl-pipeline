from typing import Dict, Any, List, Iterator
from src.interfaces.transformer_interface import DataTransformer


class ProviderTransformer(DataTransformer):
    """Transforme les données des fournisseurs de soins"""

    def transform(
        self, data: Iterator[List[Dict[str, Any]]]
    ) -> Iterator[List[Dict[str, Any]]]:
        """Transforme les données brutes des fournisseurs"""
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
        """Transforme un enregistrement de fournisseur"""
        try:
            transformed = {
                "provider_id": str(
                    record.get("provider_id", record.get("id", ""))
                ).strip(),
                "provider_name": str(record.get("provider_name", "")).strip(),
                "specialty": str(record.get("specialty", "")),
                "npi_number": str(record.get("npi_number", "")),
                "department": str(record.get("department", "")),
                "license_number": str(record.get("license_number", "")),
                "status": str(record.get("status", "active")),
            }
            return transformed
        except Exception as e:
            print(f"Error transforming provider record: {e}")
            return None

    def validate(self, record: Dict[str, Any]) -> bool:
        """Valide un enregistrement de fournisseur"""
        required_fields = ["provider_id", "provider_name"]
        for field in required_fields:
            if field not in record or not record[field]:
                return False
        return True

    def clean(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie un enregistrement de fournisseur"""
        cleaned = {}
        for key, value in record.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
                if cleaned[key] == "":
                    cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned
