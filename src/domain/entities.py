from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Patient:
    patient_id: str
    name: str
    birth_date: datetime
    gender: str
    address: Optional[str] = None


@dataclass
class Encounter:
    encounter_id: str
    patient_id: str
    encounter_date: datetime
    encounter_type: str


@dataclass
class Diagnosis:
    diagnosis_id: str
    encounter_id: str
    diagnosis_code: str
    diagnosis_description: str
    provider_id: str


@dataclass
class Provider:
    provider_id: str
    provider_name: str
    specialty: str


@dataclass
class Prescription:
    prescription_id: str
    encounter_id: str
    medication_code: str
    dosage: str
    prescribed_date: datetime
