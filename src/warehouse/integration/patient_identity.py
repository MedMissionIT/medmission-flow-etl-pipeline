# src/warehouse/integration/patient_identity.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
import hashlib
import re


class MatchConfidence(Enum):
    HIGH = "high"          # Exact match sur plusieurs critères
    MEDIUM = "medium"      # Match sur nom + date ou téléphone
    LOW = "low"           # Match possible mais incertain
    NONE = "none"         # Pas de match


@dataclass
class PatientIdentity:
    """Identité unifiée d'un patient à travers les sources"""
    
    # Identifiants uniques
    master_patient_id: str
    source_ids: Dict[str, str] = field(default_factory=dict)  # {'openmrs': '123', 'ophtalmo': 'OP-456'}
    
    # Informations démographiques standardisées
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    gender: str = ""
    birth_date: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    
    # Métadonnées
    confidence_score: float = 0.0
    match_confidence: MatchConfidence = MatchConfidence.NONE
    match_details: List[str] = field(default_factory=list)
    
    # Hash pour recherche rapide
    match_hash: str = ""
    
    def __post_init__(self):
        """Génère un hash unique pour les recherches"""
        if self.master_patient_id:
            self.match_hash = hashlib.md5(
                f"{self.master_patient_id}".encode()
            ).hexdigest()
    
    def generate_match_hash(self, attributes: List[str]) -> str:
        """Génère un hash basé sur les attributs pour matching"""
        match_string = "|".join([
            str(getattr(self, attr, "")).lower().strip()
            for attr in attributes
            if getattr(self, attr, "")
        ])
        return hashlib.md5(match_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour export"""
        return {
            'master_patient_id': self.master_patient_id,
            'openmrs_id': self.source_ids.get('openmrs', ''),
            'ophtalmo_id': self.source_ids.get('ophtalmo', ''),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'confidence_score': self.confidence_score,
            'match_confidence': self.match_confidence.value,
            'match_details': '; '.join(self.match_details)
        }