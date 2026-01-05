"""
Agent State Definition
=======================
TypedDict defining the state passed through LangGraph nodes.
"""

from typing import TypedDict, Optional, List, Dict, Any
import pandas as pd
from config.schemas import CanonicalIntent


class AgentState(TypedDict):
    """
    State passed through LangGraph nodes.
    
    This state is immutable within nodes but can be updated between nodes.
    Each node receives the current state and returns an updated state.
    
    Attributes:
        # Input
        user_query: Original user query string
        conversation_history: List of previous messages
        
        # Parsed Intent
        canonical_intent: Parsed canonical intent object
        validation_errors: List of validation error messages
        
        # Resolved Entities
        vessel_ids: List of resolved vessel IDs/MMSIs
        resolved_time_range: Resolved time range as dict with 'start' and 'end'
        
        # Execution Results
        dataframe: Pandas DataFrame with query results
        result: Final formatted result (dict, string, or other)
        
        # Metadata
        execution_log: List of execution step descriptions
        error: Error message if any step failed
    """
    # Input
    user_query: str
    conversation_history: List[Dict[str, str]]
    
    # Parsed Intent
    canonical_intent: Optional[CanonicalIntent]
"""
Agent State Definition
=======================
TypedDict defining the state passed through LangGraph nodes.
"""

from typing import TypedDict, Optional, List, Dict, Any
import pandas as pd
from config.schemas import CanonicalIntent


class AgentState(TypedDict):
    """
    State passed through LangGraph nodes.
    
    This state is immutable within nodes but can be updated between nodes.
    Each node receives the current state and returns an updated state.
    
    Attributes:
        # Input
        user_query: Original user query string
        conversation_history: List of previous messages
        
        # Parsed Intent
        canonical_intent: Parsed canonical intent object
        validation_errors: List of validation error messages
        
        # Resolved Entities
        vessel_ids: List of resolved vessel IDs/MMSIs
        resolved_time_range: Resolved time range as dict with 'start' and 'end'
        
        # Execution Results
        dataframe: Pandas DataFrame with query results
        result: Final formatted result (dict, string, or other)
        
        # Metadata
        execution_log: List of execution step descriptions
        error: Error message if any step failed
        model_name: Name of the LLM model to use
    """
    # Input
    user_query: str
    conversation_history: List[Dict[str, str]]
    
    # Parsed Intent
    canonical_intent: Optional[CanonicalIntent]
    validation_errors: List[str]
    
    # Resolved Entities
    vessel_ids: List[str]
    resolved_time_range: Optional[Dict[str, Any]]
    
    # Execution Results
    dataframe: Optional[pd.DataFrame]
    result: Optional[Any]
    
    # Metadata
    execution_log: List[str]
    error: Optional[str]
    model_name: str


def create_initial_state(
    query: str,
    history: List[Dict[str, str]] = None,
    model_name: str = "llama3"
) -> AgentState:
    """Create initial state."""
    return {
        "user_query": query,
        "conversation_history": history or [],
        "canonical_intent": None,
        "validation_errors": [],
        "vessel_ids": [],
        "resolved_time_range": None,
        "dataframe": None,
        "result": None,
        "execution_log": [],
        "error": None,
        "model_name": model_name
    }
