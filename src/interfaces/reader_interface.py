from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, Optional


class DataReader(ABC):
    """Interface pour la lecture des données"""

    @abstractmethod
    def read(self, source: str) -> Iterator[Dict[str, Any]]:
        """
        Lit les données depuis une source

        Args:
            source: Source des données (chemin de fichier, URL, etc.)

        Returns:
            Itérateur de dictionnaires
        """
        pass

    @abstractmethod
    def validate_source(self, source: str) -> bool:
        """
        Valide que la source est accessible et lisible

        Args:
            source: Source à valider

        Returns:
            True si valide, False sinon
        """
        pass

    @abstractmethod
    def get_metadata(self, source: str) -> Dict[str, Any]:
        """
        Retourne les métadonnées de la source

        Args:
            source: Source des données

        Returns:
            Dictionnaire contenant les métadonnées
        """
        pass

    @abstractmethod
    def get_data(
        self, source: str, limit: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Lit les données avec une limite optionnelle

        Args:
            source: Source des données
            limit: Nombre maximum d'enregistrements à lire

        Returns:
            Itérateur de dictionnaires
        """
        pass
