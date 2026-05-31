from typing import Dict, Any, List, Optional
from src.interfaces.reader_interface import DataReader
from src.interfaces.writer_interface import DataWriter
from src.interfaces.transformer_interface import DataTransformer
from src.pipeline.base_pipeline import BasePipeline
from src.pipeline.steps import PipelineStep
import os


class DataPipeline(BasePipeline):
    """Pipeline de données concret pour le traitement ETL"""

    def __init__(
        self,
        reader: DataReader,
        writer: DataWriter,
        transformers: Dict[str, DataTransformer],
        steps: List[PipelineStep],
    ):
        super().__init__()
        self.reader = reader
        self.writer = writer
        self.transformers = transformers
        self.steps = steps

    def validate(self, sources: Dict[str, str]) -> bool:
        """
        Valide toutes les sources avant exécution

        Args:
            sources: Dictionnaire des sources à valider

        Returns:
            True si toutes les sources sont valides, False sinon
        """
        print("\n  Validation des sources...")
        is_valid = True

        for source_name, source_path in sources.items():
            if not source_path:
                print(f"    ✗ {source_name}: chemin non spécifié")
                is_valid = False
                continue

            if not os.path.exists(source_path):
                print(f"    ✗ {source_name}: fichier non trouvé -> {source_path}")
                is_valid = False
                continue

            try:
                # Utiliser le reader pour valider la source
                if hasattr(self.reader, "validate_source"):
                    if self.reader.validate_source(source_path):
                        print(f"    ✓ {source_name}: valide")
                    else:
                        print(f"    ✗ {source_name}: invalide")
                        is_valid = False
                else:
                    # Validation simple
                    print(f"    ✓ {source_name}: existe")
            except Exception as e:
                print(f"    ✗ {source_name}: erreur - {e}")
                is_valid = False

        return is_valid

    def execute(self, sources: Dict[str, str], output_path: str) -> Dict[str, Any]:
        """
        Exécute le pipeline étape par étape

        Args:
            sources: Dictionnaire des sources de données
            output_path: Chemin de sortie

        Returns:
            Contexte d'exécution
        """
        print("=" * 50)
        print("Démarrage du pipeline ETL")
        print("=" * 50)

        # Créer le dossier de sortie s'il n'existe pas
        os.makedirs(output_path, exist_ok=True)

        # Validation initiale
        if not self.validate(sources):
            raise ValueError(f"Validation échouée: {self.errors}")

        # Exécution des étapes
        for i, step in enumerate(self.steps, 1):
            print(f"\n--- Étape {i}/{len(self.steps)}: {step.__class__.__name__} ---")
            try:
                self.context = step.execute(
                    reader=self.reader,
                    writer=self.writer,
                    transformers=self.transformers,
                    sources=sources,
                    context=self.context,
                    output_path=output_path,
                )
                print(f"✓ Étape {i} complétée")
            except Exception as e:
                error_msg = f"Erreur à l'étape {i} ({step.__class__.__name__}): {e}"
                self.add_error(error_msg)
                raise RuntimeError(error_msg)

        # Rapport final
        print("\n" + "=" * 50)
        print("Pipeline complété avec succès!")
        print(f"  - {len(self.errors)} erreurs")
        print(f"  - {len(self.warnings)} avertissements")
        print("=" * 50)

        # Afficher un résumé des données traitées
        self._print_summary()

        return self.context

    def _print_summary(self):
        """Affiche un résumé des données traitées"""
        print("\n📊 Résumé des données traitées:")
        for key, value in self.context.items():
            if isinstance(value, list):
                print(f"  - {key}: {len(value)} enregistrements")
            elif isinstance(value, dict):
                print(f"  - {key}: {len(value)} éléments")
            elif isinstance(value, str) and value.endswith(".csv"):
                if os.path.exists(value):
                    import pandas as pd

                    try:
                        df = pd.read_csv(value)
                        print(f"  - {os.path.basename(value)}: {len(df)} lignes")
                    except:
                        print(f"  - {os.path.basename(value)}: fichier créé")
