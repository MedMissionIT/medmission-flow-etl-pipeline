import pandas as pd
import os
from typing import Dict, Any, List, Iterator, Optional
from src.interfaces.writer_interface import DataWriter


class CSVWriter(DataWriter):
    """Écrivain CSV implémentant l'interface DataWriter"""

    def __init__(self, encoding="utf-8"):
        self.encoding = encoding
        self.written_files = []

    def write(
        self, data: List[Dict[str, Any]], destination: str, mode: str = "w"
    ) -> bool:
        """
        Écrit les données dans un fichier CSV

        Args:
            data: Liste de dictionnaires à écrire
            destination: Chemin du fichier de destination
            mode: Mode d'écriture ('w' pour écraser, 'a' pour ajouter)

        Returns:
            True si réussi, False sinon
        """
        try:
            if not data:
                print(f"Warning: No data to write to {destination}")
                return False

            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            # Convertir en DataFrame et écrire
            df = pd.DataFrame(data)
            df.to_csv(destination, mode=mode, index=False, encoding=self.encoding)

            self.written_files.append(destination)
            print(f"✓ Written {len(data)} records to {destination}")
            return True

        except Exception as e:
            print(f"Error writing to {destination}: {e}")
            return False

    def write_chunked(
        self,
        data_iterator: Iterator[List[Dict[str, Any]]],
        destination: str,
        chunksize: int = 1000,
    ) -> bool:
        """
        Écrit les données par morceaux pour les gros volumes

        Args:
            data_iterator: Itérateur de lots de données
            destination: Chemin du fichier de destination
            chunksize: Taille des lots (non utilisé, gardé pour compatibilité)

        Returns:
            True si réussi, False sinon
        """
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            first_chunk = True
            total_records = 0

            for chunk in data_iterator:
                if chunk:
                    df = pd.DataFrame(chunk)
                    mode = "w" if first_chunk else "a"
                    header = first_chunk
                    df.to_csv(
                        destination,
                        mode=mode,
                        header=header,
                        index=False,
                        encoding=self.encoding,
                    )
                    total_records += len(chunk)
                    first_chunk = False

            self.written_files.append(destination)
            print(f"✓ Written {total_records} records to {destination}")
            return True

        except Exception as e:
            print(f"Error writing chunked data to {destination}: {e}")
            return False

    def validate_destination(self, destination: str) -> bool:
        """
        Valide que la destination est accessible

        Args:
            destination: Chemin de destination

        Returns:
            True si valide, False sinon
        """
        try:
            directory = os.path.dirname(destination)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # Tenter d'écrire un fichier test
            test_file = os.path.join(directory, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)

            return True
        except Exception as e:
            print(f"Invalid destination {destination}: {e}")
            return False

    def get_written_files(self) -> List[str]:
        """Retourne la liste des fichiers écrits"""
        return self.written_files
