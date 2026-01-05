from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IntentRequest(BaseModel):
    text: str
    # Optional override for candidate labels if we want to change them dynamically
    candidate_labels: Optional[List[str]] = ["show", "predict", "verify", "search", "communication", "navigation"]

class Identifiers(BaseModel):
    mmsi: Optional[str] = None
    imo: Optional[str] = None
    call_sign: Optional[str] = None

class Record(BaseModel):
    timestamp: str
    lat: float
    lon: float
    sog: float
    cog: float

class NLPResponse(BaseModel):
    intent: Optional[str]
    vessel_name: Optional[str]
    time_horizon: Optional[str]
    identifiers: Identifiers
    validation_error: Optional[str] = None
    data: Optional[List[Record]] = []
    analysis_result: Optional[str] = None
