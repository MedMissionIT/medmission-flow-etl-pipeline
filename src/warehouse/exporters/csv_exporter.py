# src/warehouse/exporters/csv_exporter.py

"""
Module d'exportation CSV pour le data warehouse.
Fournit des fonctionnalités robustes d'exportation avec gestion des erreurs,
logging, validation et support des gros volumes de données.
"""

import os
import gzip
import logging
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Union, Callable
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
import json
from abc import ABC, abstractmethod

# Configuration du logging
logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Exception personnalisée pour les erreurs d'exportation"""
    pass


class ExportConfig:
    """Configuration pour l'exportation CSV"""
    
    def __init__(
        self,
        encoding: str = 'utf-8',
        sep: str = ',',
        compression: Optional[str] = None,  # None, 'gzip', 'zip'
        index: bool = False,
        date_format: str = '%Y-%m-%d',
        datetime_format: str = '%Y-%m-%d %H:%M:%S',
        float_format: str = '%.6f',
        na_rep: str = '',
        chunksize: Optional[int] = None,  # Pour les gros fichiers
        backup: bool = True,
        backup_dir: Optional[str] = None,
        validate_schema: bool = True,
        expected_columns: Optional[Dict[str, type]] = None,
        **kwargs
    ):
        self.encoding = encoding
        self.sep = sep
        self.compression = compression
        self.index = index
        self.date_format = date_format
        self.datetime_format = datetime_format
        self.float_format = float_format
        self.na_rep = na_rep
        self.chunksize = chunksize
        self.backup = backup
        self.backup_dir = backup_dir or "backups"
        self.validate_schema = validate_schema
        self.expected_columns = expected_columns or {}
        self.extra_kwargs = kwargs


class BaseExporter(ABC):
    """Classe de base abstraite pour les exportateurs"""
    
    @abstractmethod
    def export(self, df: pd.DataFrame, path: str, **kwargs) -> bool:
        """Exporte un DataFrame"""
        pass
    
    @abstractmethod
    def export_batch(self, dfs: List[pd.DataFrame], base_path: str, **kwargs) -> List[str]:
        """Exporte plusieurs DataFrames"""
        pass


class CSVExporter(BaseExporter):
    """
    Exportateur CSV robuste et professionnel.
    
    Features:
    - Compression automatique (gzip, zip)
    - Backup avant écrasement
    - Validation de schéma
    - Export par chunks pour gros volumes
    - Métadonnées d'exportation
    - Gestion des erreurs complète
    - Logging détaillé
    - Support des DataFrames vides
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialise l'exportateur CSV.
        
        Args:
            config: Configuration d'exportation. Si None, utilise les valeurs par défaut.
        """
        self.config = config or ExportConfig()
        self._export_metadata: List[Dict[str, Any]] = []
        
        # Créer les dossiers nécessaires
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crée les dossiers nécessaires s'ils n'existent pas"""
        if self.config.backup:
            Path(self.config.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_output_path(self, path: str) -> str:
        """
        Détermine le chemin de sortie avec compression.
        
        Args:
            path: Chemin de base
            
        Returns:
            Chemin avec extension appropriée
        """
        path_obj = Path(path)
        
        if self.config.compression == 'gzip' and path_obj.suffix != '.gz':
            return str(path_obj.with_suffix(path_obj.suffix + '.gz'))
        elif self.config.compression == 'zip' and path_obj.suffix != '.zip':
            return str(path_obj.with_suffix('.zip'))
        
        return str(path_obj)
    
    def _create_backup(self, path: str):
        """
        Crée une sauvegarde du fichier existant.
        
        Args:
            path: Chemin du fichier à sauvegarder
        """
        if not self.config.backup:
            return
        
        path_obj = Path(path)
        if path_obj.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{path_obj.stem}_backup_{timestamp}{path_obj.suffix}"
            backup_path = Path(self.config.backup_dir) / backup_name
            
            try:
                import shutil
                shutil.copy2(path_obj, backup_path)
                logger.info(f"Backup created: {backup_path}")
                self._export_metadata.append({
                    'type': 'backup',
                    'original': str(path_obj),
                    'backup': str(backup_path),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"Failed to create backup for {path}: {e}")
    
    def _validate_schema(self, df: pd.DataFrame) -> bool:
        """
        Valide le schéma du DataFrame.
        
        Args:
            df: DataFrame à valider
            
        Returns:
            True si la validation passe, False sinon
        """
        if not self.config.validate_schema:
            return True
        
        if not self.config.expected_columns:
            return True
        
        missing_columns = []
        wrong_type_columns = []
        
        for col, expected_type in self.config.expected_columns.items():
            if col not in df.columns:
                missing_columns.append(col)
            elif not pd.api.types.is_dtype_equal(df[col].dtype, expected_type):
                wrong_type_columns.append(f"{col} (expected: {expected_type}, got: {df[col].dtype})")
        
        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            raise ExportError(f"Schema validation failed: missing columns {missing_columns}")
        
        if wrong_type_columns:
            logger.error(f"Wrong column types: {wrong_type_columns}")
            raise ExportError(f"Schema validation failed: {wrong_type_columns}")
        
        return True
    
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prépare le DataFrame pour l'exportation.
        
        Args:
            df: DataFrame à préparer
            
        Returns:
            DataFrame préparé
        """
        if df is None:
            raise ExportError("Cannot export None DataFrame")
        
        # Faire une copie pour ne pas modifier l'original
        df = df.copy()
        
        # Gérer les colonnes datetime
        for col in df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
            df[col] = df[col].dt.strftime(self.config.datetime_format)
        
        # Gérer les colonnes date
        for col in df.select_dtypes(include=['datetime64[D]']).columns:
            df[col] = df[col].dt.strftime(self.config.date_format)
        
        # Remplacer les NaN
        df = df.fillna(self.config.na_rep)
        
        # Gérer les infinis
        df = df.replace([np.inf, -np.inf], self.config.na_rep)
        
        return df
    
    def _export_chunked(
        self,
        df: pd.DataFrame,
        path: str,
        chunksize: int
    ) -> bool:
        """
        Exporte un DataFrame par chunks pour les gros volumes.
        
        Args:
            df: DataFrame à exporter
            path: Chemin de sortie
            chunksize: Taille des chunks
            
        Returns:
            True si succès, False sinon
        """
        try:
            total_rows = len(df)
            n_chunks = (total_rows + chunksize - 1) // chunksize
            
            logger.info(f"Exporting {total_rows} rows in {n_chunks} chunks")
            
            first_chunk = True
            for i in range(0, total_rows, chunksize):
                chunk = df.iloc[i:i+chunksize]
                chunk = self._prepare_dataframe(chunk)
                
                mode = 'w' if first_chunk else 'a'
                header = first_chunk
                
                chunk.to_csv(
                    path,
                    mode=mode,
                    header=header,
                    index=self.config.index,
                    sep=self.config.sep,
                    encoding=self.config.encoding,
                    float_format=self.config.float_format,
                    **self.config.extra_kwargs
                )
                
                first_chunk = False
                logger.debug(f"Exported chunk {i//chunksize + 1}/{n_chunks}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to export chunked data: {e}")
            raise ExportError(f"Chunked export failed: {e}")
    
    def _export_compressed(self, df: pd.DataFrame, path: str) -> bool:
        """
        Exporte avec compression.
        
        Args:
            df: DataFrame à exporter
            path: Chemin de sortie
            
        Returns:
            True si succès, False sinon
        """
        try:
            df = self._prepare_dataframe(df)
            
            if self.config.compression == 'gzip':
                with gzip.open(path, 'wt', encoding=self.config.encoding) as f:
                    df.to_csv(
                        f,
                        index=self.config.index,
                        sep=self.config.sep,
                        float_format=self.config.float_format,
                        **self.config.extra_kwargs
                    )
            elif self.config.compression == 'zip':
                # Pour zip, on écrit d'abord en CSV puis on compresse
                temp_path = path.replace('.zip', '.tmp.csv')
                df.to_csv(
                    temp_path,
                    index=self.config.index,
                    sep=self.config.sep,
                    encoding=self.config.encoding,
                    float_format=self.config.float_format,
                    **self.config.extra_kwargs
                )
                
                import zipfile
                with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(temp_path, os.path.basename(temp_path).replace('.tmp.csv', '.csv'))
                
                os.remove(temp_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to export compressed data: {e}")
            raise ExportError(f"Compressed export failed: {e}")
    
    def export(
        self,
        df: pd.DataFrame,
        path: str,
        config: Optional[ExportConfig] = None,
        **kwargs
    ) -> bool:
        """
        Exporte un DataFrame vers un fichier CSV.
        
        Args:
            df: DataFrame à exporter
            path: Chemin du fichier de sortie
            config: Configuration (écrase celle de l'instance si fournie)
            **kwargs: Paramètres supplémentaires pour to_csv
            
        Returns:
            True si l'exportation a réussi
            
        Raises:
            ExportError: Si l'exportation échoue
        """
        start_time = datetime.now()
        
        # Fusionner les configurations
        export_config = config or self.config
        for key, value in kwargs.items():
            if hasattr(export_config, key):
                setattr(export_config, key, value)
        
        try:
            # Valider le DataFrame
            if df.empty:
                logger.warning(f"Exporting empty DataFrame to {path}")
            
            # Valider le schéma
            if export_config.validate_schema:
                self._validate_schema(df)
            
            # Créer le dossier parent si nécessaire
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            # Créer la sauvegarde
            self._create_backup(path)
            
            # Déterminer le chemin final
            output_path = self._get_output_path(path)
            
            # Exporter selon la méthode
            if export_config.chunksize and len(df) > export_config.chunksize:
                success = self._export_chunked(df, output_path, export_config.chunksize)
            elif export_config.compression:
                success = self._export_compressed(df, output_path)
            else:
                df = self._prepare_dataframe(df)
                df.to_csv(
                    output_path,
                    index=export_config.index,
                    sep=export_config.sep,
                    encoding=export_config.encoding,
                    float_format=export_config.float_format,
                    **export_config.extra_kwargs
                )
                success = True
            
            # Enregistrer les métadonnées
            elapsed_time = (datetime.now() - start_time).total_seconds()
            self._export_metadata.append({
                'type': 'export',
                'path': output_path,
                'rows': len(df),
                'columns': len(df.columns),
                'size_bytes': Path(output_path).stat().st_size if Path(output_path).exists() else 0,
                'elapsed_seconds': elapsed_time,
                'timestamp': start_time.isoformat()
            })
            
            logger.info(f"Successfully exported {len(df)} rows to {output_path} ({elapsed_time:.2f}s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to {path}: {e}")
            raise ExportError(f"Export failed: {e}")
    
    def export_batch(
        self,
        dfs: Dict[str, pd.DataFrame],
        base_dir: str,
        config: Optional[ExportConfig] = None,
        name_formatter: Optional[Callable[[str], str]] = None
    ) -> List[str]:
        """
        Exporte plusieurs DataFrames.
        
        Args:
            dfs: Dictionnaire {nom: DataFrame}
            base_dir: Répertoire de base pour l'exportation
            config: Configuration (écrase celle de l'instance si fournie)
            name_formatter: Fonction pour formater les noms de fichiers
            
        Returns:
            Liste des chemins exportés
        """
        exported_paths = []
        
        for name, df in dfs.items():
            if df is None or df.empty:
                logger.warning(f"Skipping empty DataFrame: {name}")
                continue
            
            # Formater le nom du fichier
            if name_formatter:
                filename = name_formatter(name)
            else:
                filename = f"{name}.csv"
            
            filepath = os.path.join(base_dir, filename)
            
            try:
                self.export(df, filepath, config)
                exported_paths.append(filepath)
            except ExportError as e:
                logger.error(f"Failed to export {name}: {e}")
                continue
        
        logger.info(f"Exported {len(exported_paths)}/{len(dfs)} DataFrames")
        return exported_paths
    
    def export_with_metadata(
        self,
        df: pd.DataFrame,
        path: str,
        metadata: Dict[str, Any],
        **kwargs
    ) -> bool:
        """
        Exporte un DataFrame avec ses métadonnées dans un fichier JSON associé.
        
        Args:
            df: DataFrame à exporter
            path: Chemin du fichier CSV
            metadata: Métadonnées à sauvegarder
            **kwargs: Paramètres pour l'exportation
            
        Returns:
            True si l'exportation a réussi
        """
        # Exporter le CSV
        self.export(df, path, **kwargs)
        
        # Exporter les métadonnées
        metadata_path = path.replace('.csv', '_metadata.json')
        if self.config.compression:
            metadata_path = metadata_path.replace(f'.{self.config.compression}', '')
        
        metadata['export_timestamp'] = datetime.now().isoformat()
        metadata['num_rows'] = len(df)
        metadata['num_columns'] = len(df.columns)
        metadata['columns'] = list(df.columns)
        metadata['file_path'] = path
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Metadata saved to {metadata_path}")
        return True
    
    def get_export_history(self) -> pd.DataFrame:
        """
        Retourne l'historique des exportations.
        
        Returns:
            DataFrame avec l'historique
        """
        if not self._export_metadata:
            return pd.DataFrame()
        
        return pd.DataFrame(self._export_metadata)
    
    def clear_export_history(self):
        """Efface l'historique des exportations"""
        self._export_metadata = []
    
    @contextmanager
    def session(self):
        """
        Contexte manager pour une session d'exportation.
        Permet de regrouper plusieurs exportations et de faire un rapport final.
        """
        session_start = datetime.now()
        exports_count = 0
        errors = []
        
        logger.info(f"Starting export session at {session_start}")
        
        try:
            yield self
        except Exception as e:
            logger.error(f"Export session error: {e}")
            errors.append(str(e))
        finally:
            session_end = datetime.now()
            duration = (session_end - session_start).total_seconds()
            
            logger.info(f"Export session completed in {duration:.2f}s")
            logger.info(f"Total exports: {len(self._export_metadata)}")
            if errors:
                logger.error(f"Errors: {len(errors)}")
            
            # Générer un rapport de session
            self._export_metadata.append({
                'type': 'session',
                'start': session_start.isoformat(),
                'end': session_end.isoformat(),
                'duration_seconds': duration,
                'exports_count': len([m for m in self._export_metadata if m.get('type') == 'export']),
                'errors': errors
            })


class DatabaseExporter(BaseExporter):
    """Exportateur vers base de données"""
    
    def __init__(self, connection_string: str, if_exists: str = 'replace'):
        """
        Initialise l'exportateur base de données.
        
        Args:
            connection_string: Chaîne de connexion SQLAlchemy
            if_exists: Comportement si la table existe ('fail', 'replace', 'append')
        """
        from sqlalchemy import create_engine
        self.engine = create_engine(connection_string)
        self.if_exists = if_exists
        logger.info(f"Database exporter initialized with {connection_string}")
    
    def export(self, df: pd.DataFrame, table_name: str, **kwargs) -> bool:
        """
        Exporte un DataFrame vers une table SQL.
        
        Args:
            df: DataFrame à exporter
            table_name: Nom de la table
            **kwargs: Paramètres supplémentaires pour to_sql
            
        Returns:
            True si succès
        """
        try:
            df.to_sql(
                table_name,
                self.engine,
                if_exists=kwargs.get('if_exists', self.if_exists),
                index=kwargs.get('index', False),
                chunksize=kwargs.get('chunksize', 1000),
                method=kwargs.get('method', None)
            )
            logger.info(f"Exported {len(df)} rows to table {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to export to {table_name}: {e}")
            raise ExportError(f"Database export failed: {e}")
    
    def export_batch(self, dfs: Dict[str, pd.DataFrame], **kwargs) -> List[str]:
        """
        Exporte plusieurs DataFrames vers des tables.
        
        Args:
            dfs: Dictionnaire {table_name: DataFrame}
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Liste des tables exportées
        """
        exported_tables = []
        
        for table_name, df in dfs.items():
            if df is None or df.empty:
                logger.warning(f"Skipping empty DataFrame for table {table_name}")
                continue
            
            try:
                self.export(df, table_name, **kwargs)
                exported_tables.append(table_name)
            except ExportError as e:
                logger.error(f"Failed to export {table_name}: {e}")
        
        return exported_tables


class MultiFormatExporter(BaseExporter):
    """Exportateur multi-format (CSV, Excel, Parquet, JSON)"""
    
    def __init__(self, default_format: str = 'csv'):
        """
        Initialise l'exportateur multi-format.
        
        Args:
            default_format: Format par défaut ('csv', 'excel', 'parquet', 'json')
        """
        self.default_format = default_format
        self.csv_exporter = CSVExporter()
    
    def export(
        self,
        df: pd.DataFrame,
        path: str,
        format: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Exporte un DataFrame dans le format spécifié.
        
        Args:
            df: DataFrame à exporter
            path: Chemin du fichier
            format: Format d'exportation
            **kwargs: Paramètres spécifiques au format
            
        Returns:
            True si succès
        """
        export_format = format or self.default_format
        
        if export_format == 'csv':
            return self.csv_exporter.export(df, path, **kwargs)
        elif export_format == 'excel':
            df.to_excel(path, index=kwargs.get('index', False), **kwargs)
            return True
        elif export_format == 'parquet':
            df.to_parquet(path, index=kwargs.get('index', False), **kwargs)
            return True
        elif export_format == 'json':
            df.to_json(path, orient=kwargs.get('orient', 'records'), **kwargs)
            return True
        else:
            raise ExportError(f"Unsupported format: {export_format}")
    
    def export_batch(self, dfs: Dict[str, pd.DataFrame], base_dir: str, **kwargs) -> List[str]:
        """
        Exporte plusieurs DataFrames.
        
        Args:
            dfs: Dictionnaire {nom: DataFrame}
            base_dir: Répertoire de base
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Liste des chemins exportés
        """
        exported_paths = []
        
        for name, df in dfs.items():
            path = os.path.join(base_dir, f"{name}.{self.default_format}")
            try:
                self.export(df, path, **kwargs)
                exported_paths.append(path)
            except ExportError as e:
                logger.error(f"Failed to export {name}: {e}")
        
        return exported_paths


# Fonctions utilitaires pour une utilisation rapide

def quick_export(
    df: pd.DataFrame,
    path: str,
    **kwargs
) -> bool:
    """
    Fonction rapide pour exporter un CSV avec configuration par défaut.
    
    Args:
        df: DataFrame à exporter
        path: Chemin du fichier
        **kwargs: Paramètres supplémentaires
        
    Returns:
        True si succès
    """
    exporter = CSVExporter()
    return exporter.export(df, path, **kwargs)


def export_with_backup(
    df: pd.DataFrame,
    path: str,
    backup_dir: str = "backups",
    **kwargs
) -> bool:
    """
    Exporte avec backup automatique.
    
    Args:
        df: DataFrame à exporter
        path: Chemin du fichier
        backup_dir: Dossier de backup
        **kwargs: Paramètres supplémentaires
    """
    config = ExportConfig(backup=True, backup_dir=backup_dir)
    exporter = CSVExporter(config)
    return exporter.export(df, path, **kwargs)


def export_large_dataset(
    df: pd.DataFrame,
    path: str,
    chunksize: int = 100000,
    compression: str = 'gzip',
    **kwargs
) -> bool:
    """
    Exporte un gros dataset par chunks avec compression.
    
    Args:
        df: DataFrame à exporter
        path: Chemin du fichier
        chunksize: Taille des chunks
        compression: Type de compression
        **kwargs: Paramètres supplémentaires
    """
    config = ExportConfig(chunksize=chunksize, compression=compression)
    exporter = CSVExporter(config)
    return exporter.export(df, path, **kwargs)


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Exemple 1: Export simple
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
    quick_export(df, "test_output/simple.csv")
    
    # Exemple 2: Export avec configuration personnalisée
    config = ExportConfig(
        sep=';',
        encoding='utf-8-sig',
        compression='gzip',
        backup=True,
        validate_schema=True,
        expected_columns={'col1': 'int64', 'col2': 'object'}
    )
    exporter = CSVExporter(config)
    exporter.export(df, "test_output/custom.csv.gz")
    
    # Exemple 3: Export batch
    dfs = {
        'table1': pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']}),
        'table2': pd.DataFrame({'id': [3, 4], 'value': [10, 20]})
    }
    exporter.export_batch(dfs, "test_output/batch")
    
    # Exemple 4: Export avec métadonnées
    metadata = {
        'source': 'OpenMRS',
        'version': '1.0',
        'description': 'Patient master data'
    }
    exporter.export_with_metadata(df, "test_output/with_metadata.csv", metadata)
    
    # Exemple 5: Utilisation du contexte
    with exporter.session():
        exporter.export(df, "test_output/session1.csv")
        exporter.export(df, "test_output/session2.csv")
    
    # Afficher l'historique
    history = exporter.get_export_history()
    print("\nExport History:")
    print(history)