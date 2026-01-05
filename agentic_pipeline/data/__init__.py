"""Data package initialization."""

from .duckdb_manager import DuckDBManager
from .parquet_loader import ParquetLoader

__all__ = [
    "DuckDBManager",
    "ParquetLoader",
]
