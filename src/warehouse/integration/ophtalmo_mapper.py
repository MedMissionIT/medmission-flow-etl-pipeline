# src/warehouse/integration/ophtalmo_mapper.py
import pandas as pd
import re
from typing import Dict, List, Optional
from .patient_identity import PatientIdentity


class OphtalmoMapper:
    """Mapper spécifique pour les données d'ophtalmologie"""
    
    def __init__(self):
        self.field_mappings = {
            'NOM': 'last_name',
            'PRENOM': 'first_name',
            'DATE_NAISSANCE': 'birth_date',
            'SEXE': 'gender',
            'TELEPHONE': 'phone',
            'ID_PATIENT': 'patient_id'
        }
    
    def map_to_standard_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convertit le format ophtalmologie vers format standard"""
        mapped_df = pd.DataFrame()
        
        for source_col, target_col in self.field_mappings.items():
            if source_col in df.columns:
                mapped_df[target_col] = df[source_col]
            else:
                # Cherche des variations
                found = self._find_similar_column(df.columns, source_col)
                if found:
                    mapped_df[target_col] = df[found]
        
        # Créer full_name
        if 'first_name' in mapped_df and 'last_name' in mapped_df:
            mapped_df['full_name'] = mapped_df['first_name'] + ' ' + mapped_df['last_name']
        elif 'last_name' in mapped_df:
            mapped_df['full_name'] = mapped_df['last_name']
        elif 'first_name' in mapped_df:
            mapped_df['full_name'] = mapped_df['first_name']
        
        # Normaliser le genre
        if 'gender' in mapped_df:
            mapped_df['gender'] = mapped_df['gender'].apply(self._normalize_gender)
        
        # Normaliser la date
        if 'birth_date' in mapped_df:
            mapped_df['birth_date'] = pd.to_datetime(mapped_df['birth_date'], errors='coerce')
        
        return mapped_df
    
    def extract_patients_from_excel(self, excel_path: str) -> pd.DataFrame:
        """Extrait les patients d'un fichier Excel ophtalmologie"""
        df = pd.read_excel(excel_path)
        
        # Identifie automatiquement les colonnes pertinentes
        identified_columns = self._identify_columns(df.columns)
        
        # Crée un DataFrame standardisé
        standardized = pd.DataFrame()
        for std_col, source_col in identified_columns.items():
            if source_col in df.columns:
                standardized[std_col] = df[source_col]
        
        return standardized
    
    def _identify_columns(self, columns: List[str]) -> Dict[str, str]:
        """Identifie automatiquement les colonnes"""
        mapping = {}
        
        # Patterns pour chaque type de colonne
        patterns = {
            'patient_id': [r'(?i)^id$', r'(?i)^patient', r'(?i)^numer'],
            'first_name': [r'(?i)^prenom', r'(?i)^first', r'(?i)^given'],
            'last_name': [r'(?i)^nom', r'(?i)^last', r'(?i)^family'],
            'birth_date': [r'(?i)^date.*naissance', r'(?i)^birth', r'(?i)^dob'],
            'gender': [r'(?i)^sexe', r'(?i)^gender'],
            'phone': [r'(?i)^tel', r'(?i)^phone', r'(?i)^mobile']
        }
        
        for std_col, patterns_list in patterns.items():
            for col in columns:
                for pattern in patterns_list:
                    if re.match(pattern, col, re.IGNORECASE):
                        mapping[std_col] = col
                        break
                if std_col in mapping:
                    break
        
        return mapping
    
    def _normalize_gender(self, gender: str) -> str:
        """Normalise les valeurs de genre"""
        if pd.isna(gender):
            return "Unknown"
        
        gender_str = str(gender).upper().strip()
        if gender_str in ['M', 'MASCULIN', 'HOMME', 'MALE']:
            return 'M'
        elif gender_str in ['F', 'FEMININ', 'FEMME', 'FEMALE']:
            return 'F'
        else:
            return 'Unknown'
    
    def _find_similar_column(self, columns: List[str], target: str) -> Optional[str]:
        """Trouve une colonne similaire"""
        target_lower = target.lower()
        for col in columns:
            if target_lower in col.lower():
                return col
        return None