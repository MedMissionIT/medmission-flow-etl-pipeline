from abc import ABC, abstractmethod
from typing import Dict, Any, List, Iterator, Optional


class DataTransformer(ABC):
    """Interface abstraite pour tous les transformateurs de données"""

    @abstractmethod
    def transform(
        self, data: Iterator[List[Dict[str, Any]]]
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Transforme les données brutes en données nettoyées

        Args:
            data: Itérateur de lots de données brutes

        Returns:
            Itérateur de lots de données transformées
        """
        pass

    @abstractmethod
    def validate(self, record: Dict[str, Any]) -> bool:
        """
        Valide un enregistrement avant transformation

        Args:
            record: Enregistrement à valider

        Returns:
            True si valide, False sinon
        """
        pass

    @abstractmethod
    def clean(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nettoie un enregistrement

        Args:
            record: Enregistrement à nettoyer

        Returns:
            Enregistrement nettoyé
        """
        pass
