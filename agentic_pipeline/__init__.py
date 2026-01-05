"""
Agentic Orchestration Pipeline for Maritime AIS Intelligence
=============================================================

A production-ready, modular agentic pipeline for maritime AIS analytics using
LangGraph, DuckDB, and ML models.

Key Features:
- Multi-level intent understanding (trajectory, loitering, prediction, listing)
- Entity resolution across conversation context
- Safe orchestration of database queries, geospatial tools, and ML models
- Deterministic execution with LLMs used strictly as planners

Author: Maritime Intelligence Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Maritime Intelligence Team"

from .core.graph import create_orchestration_graph
from .core.state import AgentState
from .config.schemas import CanonicalIntent

__all__ = [
    "create_orchestration_graph",
    "AgentState",
    "CanonicalIntent",
]
