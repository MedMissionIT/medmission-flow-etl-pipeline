from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePipeline(ABC):
    """Classe abstraite de base pour tous les pipelines"""

    def __init__(self):
        self.context = {}
        self.errors = []
        self.warnings = []

    @abstractmethod
    def execute(self, sources: Dict[str, str], output_path: str) -> Dict[str, Any]:
        """
        Exécute le pipeline

        Args:
            sources: Dictionnaire des sources de données
            output_path: Chemin de sortie pour les résultats

        Returns:
            Dictionnaire contenant le contexte d'exécution
        """
        pass

    @abstractmethod
    def validate(self, sources: Dict[str, str]) -> bool:
        """
        Valide les sources avant exécution

        Args:
            sources: Dictionnaire des sources à valider

        Returns:
            True si valide, False sinon
        """
        pass

    def add_error(self, error: str):
        """Ajoute une erreur au journal"""
        self.errors.append(error)
        print(f"  ❌ Erreur: {error}")

    def add_warning(self, warning: str):
        """Ajoute un avertissement au journal"""
        self.warnings.append(warning)
        print(f"  ⚠ Avertissement: {warning}")

    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'exécution"""
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "context_keys": list(self.context.keys()),
        }

    def clear(self):
        """Nettoie le contexte et les erreurs"""
        self.context = {}
        self.errors = []
        self.warnings = []
