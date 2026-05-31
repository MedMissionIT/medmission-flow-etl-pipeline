import pandas as pd
from typing import Iterator, Dict, Any, Optional
from src.interfaces.reader_interface import DataReader


class CSVReader(DataReader):
    """Lecteur CSV implémentant l'interface DataReader"""

    def __init__(self, chunksize: int = 10000):
        self.chunksize = chunksize
        self.metadata = {}

    def read(self, source: str) -> Iterator[Dict[str, Any]]:
        """
        Lit un fichier CSV et retourne un itérateur de dictionnaires

        Args:
            source: Chemin du fichier CSV

        Yields:
            Dictionnaire représentant chaque ligne
        """
        try:
            for chunk in pd.read_csv(source, chunksize=self.chunksize):
                for record in chunk.to_dict("records"):
                    yield record
        except Exception as e:
            print(f"Erreur lors de la lecture de {source}: {e}")
            return

    def validate_source(self, source: str) -> bool:
        """
        Valide que la source CSV est accessible et lisible

        Args:
            source: Chemin du fichier CSV

        Returns:
            True si valide, False sinon
        """
        try:
            # Vérifier si le fichier existe
            import os

            if not os.path.exists(source):
                print(f"Fichier non trouvé: {source}")
                return False

            # Tenter de lire la première ligne
            df = pd.read_csv(source, nrows=1)
            return True
        except Exception as e:
            print(f"Erreur de validation de {source}: {e}")
            return False

    def get_metadata(self, source: str) -> Dict[str, Any]:
        """
        Retourne les métadonnées du fichier CSV

        Args:
            source: Chemin du fichier CSV

        Returns:
            Dictionnaire contenant les métadonnées
        """
        try:
            # Lire les premières lignes pour analyser la structure
            df_sample = pd.read_csv(source, nrows=100)

            metadata = {
                "source": source,
                "columns": list(df_sample.columns),
                "column_count": len(df_sample.columns),
                "dtypes": df_sample.dtypes.astype(str).to_dict(),
                "sample_rows": 100,
                "file_size": self._get_file_size(source),
            }

            return metadata
        except Exception as e:
            print(f"Erreur lors de la récupération des métadonnées: {e}")
            return {"source": source, "error": str(e)}

    def get_data(
        self, source: str, limit: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Lit les données avec une limite optionnelle

        Args:
            source: Chemin du fichier CSV
            limit: Nombre maximum de lignes à lire

        Yields:
            Dictionnaire représentant chaque ligne
        """
        try:
            if limit:
                df = pd.read_csv(source, nrows=limit)
                for record in df.to_dict("records"):
                    yield record
            else:
                for record in self.read(source):
                    yield record
        except Exception as e:
            print(f"Erreur lors de la lecture des données: {e}")
            return

    def _get_file_size(self, source: str) -> str:
        """Retourne la taille du fichier en format lisible"""
        import os

        try:
            size_bytes = os.path.getsize(source)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
        except:
            return "Inconnue"
