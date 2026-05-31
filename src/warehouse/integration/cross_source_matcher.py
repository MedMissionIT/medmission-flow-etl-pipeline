# src/warehouse/integration/cross_source_matcher.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from rapidfuzz import fuzz, process
from datetime import datetime
import logging
from .patient_identity import PatientIdentity, MatchConfidence

logger = logging.getLogger(__name__)


class CrossSourceMatcher:
    """Match les patients entre OpenMRS et sources externes (Ophtalmologie)"""
    
    def __init__(self, threshold_high: float = 0.9, threshold_medium: float = 0.7):
        self.threshold_high = threshold_high
        self.threshold_medium = threshold_medium
        
        # Pondérations pour différents critères
        self.weights = {
            'full_name': 0.30,
            'first_name': 0.20,
            'last_name': 0.20,
            'birth_date': 0.20,
            'phone': 0.10
        }
    
    def match_patients(
        self, 
        openmrs_patients: pd.DataFrame, 
        external_patients: pd.DataFrame,
        source_name: str = "external"
    ) -> List[PatientIdentity]:
        """Match les patients entre OpenMRS et une source externe"""
        
        master_patients = []
        matched_openmrs_ids = set()
        matched_external_ids = set()
        
        # 1. D'abord, chercher des matches exacts
        exact_matches = self._find_exact_matches(openmrs_patients, external_patients)
        
        # 2. Ensuite, matches probabilistes
        fuzzy_matches = self._find_fuzzy_matches(
            openmrs_patients, 
            external_patients, 
            exact_matches
        )
        
        # 3. Créer les entités patient unifiées
        all_matches = {**exact_matches, **fuzzy_matches}
        
        for (openmrs_idx, external_idx), score in all_matches.items():
            openmrs_id = openmrs_patients.iloc[openmrs_idx].get('patient_id', str(openmrs_idx))
            external_id = external_patients.iloc[external_idx].get('patient_id', str(external_idx))
            
            matched_openmrs_ids.add(openmrs_idx)
            matched_external_ids.add(external_idx)
            
            patient = self._create_unified_patient(
                openmrs_patients.iloc[openmrs_idx],
                external_patients.iloc[external_idx],
                score,
                source_name
            )
            master_patients.append(patient)
        
        # 4. Ajouter les patients non-matchés (uniquement dans une source)
        master_patients.extend(
            self._add_unmatched_patients(
                openmrs_patients, 
                external_patients, 
                matched_openmrs_ids, 
                matched_external_ids,
                source_name
            )
        )
        
        logger.info(f"Matched {len(exact_matches)} exact + {len(fuzzy_matches)} fuzzy matches")
        logger.info(f"Total patients: {len(master_patients)}")
        
        return master_patients
    
    def _find_exact_matches(
        self, 
        openmrs_patients: pd.DataFrame, 
        external_patients: pd.DataFrame
    ) -> Dict[Tuple[int, int], float]:
        """Trouve des matches exacts sur plusieurs critères"""
        matches = {}
        
        for i, openmrs_patient in openmrs_patients.iterrows():
            for j, external_patient in external_patients.iterrows():
                score = self._calculate_exact_match_score(openmrs_patient, external_patient)
                if score >= self.threshold_high:
                    matches[(i, j)] = score
                    
        return matches
    
    def _find_fuzzy_matches(
        self,
        openmrs_patients: pd.DataFrame,
        external_patients: pd.DataFrame,
        exact_matches: Dict
    ) -> Dict[Tuple[int, int], float]:
        """Trouve des matches probabilistes"""
        matches = {}
        
        # Index des patients déjà matchés
        matched_openmrs = set([m[0] for m in exact_matches.keys()])
        matched_external = set([m[1] for m in exact_matches.keys()])
        
        for i, openmrs_patient in openmrs_patients.iterrows():
            if i in matched_openmrs:
                continue
                
            best_match = None
            best_score = 0
            
            for j, external_patient in external_patients.iterrows():
                if j in matched_external:
                    continue
                    
                score = self._calculate_fuzzy_match_score(openmrs_patient, external_patient)
                
                if score > best_score and score >= self.threshold_medium:
                    best_score = score
                    best_match = j
            
            if best_match is not None:
                matches[(i, best_match)] = best_score
                matched_openmrs.add(i)
                matched_external.add(best_match)
        
        return matches
    
    def _calculate_exact_match_score(
        self, 
        openmrs_patient: pd.Series, 
        external_patient: pd.Series
    ) -> float:
        """Calcule le score pour match exact"""
        score = 0.0
        
        # Nom complet
        if self._normalize_text(openmrs_patient.get('full_name', '')) == \
           self._normalize_text(external_patient.get('full_name', '')):
            score += self.weights['full_name']
        
        # Date de naissance
        if str(openmrs_patient.get('birth_date', '')) == \
           str(external_patient.get('birth_date', '')):
            score += self.weights['birth_date']
        
        # Téléphone
        if self._normalize_phone(openmrs_patient.get('phone', '')) == \
           self._normalize_phone(external_patient.get('phone', '')):
            score += self.weights['phone']
        
        return score
    
    def _calculate_fuzzy_match_score(
        self,
        openmrs_patient: pd.Series,
        external_patient: pd.Series
    ) -> float:
        """Calcule le score pour match flou"""
        score = 0.0
        
        # Nom flou
        openmrs_name = self._normalize_text(openmrs_patient.get('full_name', ''))
        external_name = self._normalize_text(external_patient.get('full_name', ''))
        
        if openmrs_name and external_name:
            name_score = fuzz.ratio(openmrs_name, external_name) / 100
            score += name_score * self.weights['full_name']
        
        # Prénom + Nom
        openmrs_first = self._normalize_text(openmrs_patient.get('first_name', ''))
        external_first = self._normalize_text(external_patient.get('first_name', ''))
        
        if openmrs_first and external_first:
            first_score = fuzz.ratio(openmrs_first, external_first) / 100
            score += first_score * self.weights['first_name']
        
        # Date de naissance (exact ou proche)
        if self._dates_close(
            openmrs_patient.get('birth_date', ''),
            external_patient.get('birth_date', '')
        ):
            score += self.weights['birth_date']
        
        return score
    
    def _create_unified_patient(
        self,
        openmrs_patient: pd.Series,
        external_patient: pd.Series,
        match_score: float,
        source_name: str
    ) -> PatientIdentity:
        """Crée un patient unifié à partir des matches"""
        
        # Déterminer la confiance du match
        if match_score >= self.threshold_high:
            confidence = MatchConfidence.HIGH
        elif match_score >= self.threshold_medium:
            confidence = MatchConfidence.MEDIUM
        else:
            confidence = MatchConfidence.LOW
        
        # Générer ID maître
        master_id = self._generate_master_id(openmrs_patient, external_patient)
        
        # Prendre les meilleures valeurs de chaque source
        first_name = self._best_value(
            openmrs_patient.get('first_name', ''),
            external_patient.get('first_name', '')
        )
        last_name = self._best_value(
            openmrs_patient.get('last_name', ''),
            external_patient.get('last_name', '')
        )
        
        patient = PatientIdentity(
            master_patient_id=master_id,
            source_ids={
                'openmrs': str(openmrs_patient.get('patient_id', '')),
                source_name: str(external_patient.get('patient_id', ''))
            },
            first_name=first_name,
            last_name=last_name,
            full_name=f"{first_name} {last_name}".strip(),
            gender=openmrs_patient.get('gender', ''),
            birth_date=str(openmrs_patient.get('birth_date', '')),
            phone=self._best_value(
                openmrs_patient.get('phone', ''),
                external_patient.get('phone', '')
            ),
            email=openmrs_patient.get('email', ''),
            confidence_score=match_score,
            match_confidence=confidence,
            match_details=[f"Matched with score: {match_score:.2f}"]
        )
        
        return patient
    
    def _add_unmatched_patients(
        self,
        openmrs_patients: pd.DataFrame,
        external_patients: pd.DataFrame,
        matched_openmrs: set,
        matched_external: set,
        source_name: str
    ) -> List[PatientIdentity]:
        """Ajoute les patients non-matchés"""
        unmatched = []
        
        # OpenMRS patients non-matchés
        for i, patient in openmrs_patients.iterrows():
            if i not in matched_openmrs:
                master_id = f"OPENMRS_{patient.get('patient_id', i)}"
                unmatched.append(PatientIdentity(
                    master_patient_id=master_id,
                    source_ids={'openmrs': str(patient.get('patient_id', i))},
                    full_name=patient.get('full_name', ''),
                    first_name=patient.get('first_name', ''),
                    last_name=patient.get('last_name', ''),
                    gender=patient.get('gender', ''),
                    birth_date=str(patient.get('birth_date', '')),
                    match_confidence=MatchConfidence.NONE,
                    confidence_score=0.0
                ))
        
        # Patients externes non-matchés
        for j, patient in external_patients.iterrows():
            if j not in matched_external:
                master_id = f"{source_name.upper()}_{patient.get('patient_id', j)}"
                unmatched.append(PatientIdentity(
                    master_patient_id=master_id,
                    source_ids={source_name: str(patient.get('patient_id', j))},
                    full_name=patient.get('full_name', ''),
                    first_name=patient.get('first_name', ''),
                    last_name=patient.get('last_name', ''),
                    gender=patient.get('gender', ''),
                    birth_date=str(patient.get('birth_date', '')),
                    match_confidence=MatchConfidence.NONE,
                    confidence_score=0.0
                ))
        
        return unmatched
    
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour comparaison"""
        if pd.isna(text) or text is None:
            return ""
        return str(text).lower().strip().replace(' ', '').replace('-', '')
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalise les numéros de téléphone"""
        if pd.isna(phone) or phone is None:
            return ""
        # Garde uniquement les chiffres
        return re.sub(r'\D', '', str(phone))
    
    def _dates_close(self, date1: str, date2: str, max_diff_days: int = 7) -> bool:
        """Vérifie si deux dates sont proches"""
        try:
            d1 = pd.to_datetime(date1)
            d2 = pd.to_datetime(date2)
            return abs((d1 - d2).days) <= max_diff_days
        except:
            return False
    
    def _best_value(self, val1: str, val2: str) -> str:
        """Choisit la meilleure valeur entre deux sources"""
        if pd.isna(val1) or not val1:
            return val2 if not pd.isna(val2) else ""
        if pd.isna(val2) or not val2:
            return val1
        # Si les deux existent, choisir la plus longue
        return val1 if len(str(val1)) >= len(str(val2)) else val2
    
    def _generate_master_id(self, openmrs: pd.Series, external: pd.Series) -> str:
        """Génère un ID maître unique"""
        # Utilise l'ID OpenMRS si disponible, sinon combine les IDs
        openmrs_id = openmrs.get('patient_id', '')
        external_id = external.get('patient_id', '')
        
        if openmrs_id:
            return f"MPI_{openmrs_id}"
        else:
            return f"MPI_{external_id}"