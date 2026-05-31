# tests/integration/test_master_patient_index.py
import pytest
import pandas as pd
from src.warehouse.integration import CrossSourceMatcher, PatientIdentity


def test_cross_source_matching():
    """Teste le matching cross-source"""
    
    # Données OpenMRS
    openmrs_data = pd.DataFrame({
        'patient_id': ['1001', '1002', '1003', '1004'],
        'first_name': ['Jean', 'Marie', 'Pierre', 'Sophie'],
        'last_name': ['Dupont', 'Martin', 'Bernard', 'Petit'],
        'full_name': ['Jean Dupont', 'Marie Martin', 'Pierre Bernard', 'Sophie Petit'],
        'birth_date': ['1980-01-01', '1990-02-02', '1975-03-03', '1985-04-04'],
        'phone': ['691234567', '692345678', '693456789', '694567890'],
        'gender': ['M', 'F', 'M', 'F']
    })
    
    # Données Ophtalmologie
    ophtalmo_data = pd.DataFrame({
        'patient_id': ['OP001', 'OP002', 'OP003'],
        'first_name': ['Jean', 'Marie', 'Jacques'],
        'last_name': ['Dupont', 'Martin', 'Durand'],
        'full_name': ['Jean Dupont', 'Marie Martin', 'Jacques Durand'],
        'birth_date': ['1980-01-01', '1990-02-02', '1978-05-05'],
        'phone': ['691234567', '692345678', '695678901'],
        'gender': ['M', 'F', 'M']
    })
    
    # Matcher
    matcher = CrossSourceMatcher(threshold_high=0.85, threshold_medium=0.65)
    matches = matcher.match_patients(openmrs_data, ophtalmo_data, "ophtalmo")
    
    # Vérifications
    assert len(matches) > 0
    
    # Vérifier les matches
    matched_patients = [p for p in matches if p.match_confidence != MatchConfidence.NONE]
    assert len(matched_patients) >= 2  # Jean et Marie devraient matcher
    
    # Vérifier les IDs sources
    for patient in matched_patients:
        assert 'openmrs' in patient.source_ids or 'ophtalmo' in patient.source_ids


def test_patient_identity_creation():
    """Teste la création d'identité patient"""
    
    patient = PatientIdentity(
        master_patient_id="MPI_001",
        source_ids={'openmrs': '1001', 'ophtalmo': 'OP001'},
        first_name="Jean",
        last_name="Dupont",
        full_name="Jean Dupont",
        gender="M",
        birth_date="1980-01-01"
    )
    
    assert patient.master_patient_id == "MPI_001"
    assert patient.source_ids['openmrs'] == '1001'
    assert patient.match_hash is not None
    
    # Test conversion dict
    patient_dict = patient.to_dict()
    assert patient_dict['master_patient_id'] == "MPI_001"
    assert patient_dict['match_confidence'] == "none"