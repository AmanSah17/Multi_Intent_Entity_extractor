"""
Canonical Intent & Entity Schema
=================================
Pydantic models enforcing the canonical schema for all LLM outputs.
This ensures safety, determinism, and schema validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime


class VesselIdentifier(BaseModel):
    """
    Vessel identification schema.
    
    Attributes:
        imo: International Maritime Organization number
        mmsi: Maritime Mobile Service Identity
        name: Vessel name
    """
    imo: Optional[str] = None
    mmsi: Optional[str] = None
    name: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "imo": "9876543",
                "mmsi": "123456789",
                "name": "INS Kolkata"
            }
        }


class TimeConstraint(BaseModel):
    """
    Time filtering constraints.
    
    Attributes:
        mode: Time specification mode (relative or absolute)
        relative: Relative time expression (e.g., "last_6h", "last_weekend")
        start: Absolute start datetime
        end: Absolute end datetime
    """
    mode: Literal["relative", "absolute"] = "relative"
    relative: Optional[str] = None
    start: Optional[str] = None  # ISO format datetime string
    end: Optional[str] = None    # ISO format datetime string
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "mode": "relative",
                    "relative": "last_6h",
                    "start": None,
                    "end": None
                },
                {
                    "mode": "absolute",
                    "relative": None,
                    "start": "2020-01-05T00:00:00",
                    "end": "2020-01-12T23:59:59"
                }
            ]
        }


class SpatialConstraint(BaseModel):
    """
    Spatial filtering constraints.
    
    Attributes:
        type: Type of spatial constraint
        distance_nm: Distance from coast in nautical miles
        polygon_type: Type of polygon (EEZ, TTW, fishing_zone)
        polygon_id: Identifier for the specific polygon
    """
    type: Literal["none", "coastal_distance", "polygon"] = "none"
    distance_nm: Optional[float] = None
    polygon_type: Optional[str] = None
    polygon_id: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "type": "coastal_distance",
                    "distance_nm": 12.0,
                    "polygon_type": None,
                    "polygon_id": None
                },
                {
                    "type": "polygon",
                    "distance_nm": None,
                    "polygon_type": "EEZ",
                    "polygon_id": "IND_EEZ_001"
                }
            ]
        }


class ExecutionMode(BaseModel):
    """
    Execution configuration.
    
    Attributes:
        data_source: Source of data (raw AIS, ML predictions, or model inference)
        model_name: Name of ML model to use (if applicable)
    """
    data_source: Literal["raw_ais", "ml_predictions", "model_inference"] = "raw_ais"
    model_name: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "data_source": "raw_ais",
                    "model_name": None
                },
                {
                    "data_source": "model_inference",
                    "model_name": "trajectory_predictor_v1"
                }
            ]
        }


class OutputConfig(BaseModel):
    """
    Output formatting configuration.
    
    Attributes:
        format: Output format (map, table, or summary)
        limit: Maximum number of results to return
    """
    format: Literal["map", "table", "summary"] = "table"
    limit: int = Field(default=50, ge=1, le=10000)
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "format": "table",
                "limit": 50
            }
        }


class CanonicalIntent(BaseModel):
    """
    Canonical intent schema enforced for all LLM outputs.
    
    This schema ensures:
    - Safety: No code execution, only structured data
    - Determinism: Clear, validated intent structure
    - Explainability: Human-readable intent representation
    
    Attributes:
        domain_intent: High-level domain (trajectory, loitering, prediction, listing)
        task_intent: Specific task (show, predict, detect, list)
        vessel_scope: Scope of vessels (single, multiple, all)
        vessels: List of vessel identifiers
        time_constraint: Time filtering constraints
        spatial_constraint: Spatial filtering constraints
        execution_mode: Execution configuration
        output: Output formatting configuration
    """
    domain_intent: Literal["trajectory", "loitering", "prediction", "listing"]
    task_intent: Literal["show", "predict", "detect", "list"]
    vessel_scope: Literal["single", "multiple", "all"]
    vessels: List[VesselIdentifier] = Field(default_factory=list)
    time_constraint: TimeConstraint = Field(default_factory=TimeConstraint)
    spatial_constraint: SpatialConstraint = Field(default_factory=SpatialConstraint)
    execution_mode: ExecutionMode = Field(default_factory=ExecutionMode)
    output: OutputConfig = Field(default_factory=OutputConfig)
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "domain_intent": "trajectory",
                "task_intent": "show",
                "vessel_scope": "single",
                "vessels": [
                    {
                        "imo": None,
                        "mmsi": "123456789",
                        "name": None
                    }
                ],
                "time_constraint": {
                    "mode": "relative",
                    "relative": "last_6h",
                    "start": None,
                    "end": None
                },
                "spatial_constraint": {
                    "type": "none",
                    "distance_nm": None,
                    "polygon_type": None,
                    "polygon_id": None
                },
                "execution_mode": {
                    "data_source": "raw_ais",
                    "model_name": None
                },
                "output": {
                    "format": "table",
                    "limit": 50
                }
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=2)
