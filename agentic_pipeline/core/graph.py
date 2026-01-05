"""
LangGraph Orchestration
========================
Main orchestration graph with all pipeline nodes.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from datetime import datetime

from core.state import AgentState
from services.memory_manager import MemoryManager
from services.intent_parser import IntentParser
from services.plan_validator import PlanValidator
from services.vessel_resolver import VesselResolver
from services.trajectory_service import TrajectoryService
from services.loitering_service import LoiteringService
from services.response_builder import ResponseBuilder
from data.duckdb_manager import DuckDBManager
from data.parquet_loader import ParquetLoader
from config.settings import settings
from utils.validators import parse_relative_time
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize services (singleton pattern)
_db_manager = None
_memory_manager = None
_intent_parser = None
_plan_validator = None
_vessel_resolver = None
_trajectory_service = None
_loitering_service = None
_response_builder = None


def _initialize_services():
    """Initialize all services (lazy initialization)."""
    global _db_manager, _memory_manager, _intent_parser, _plan_validator
    global _vessel_resolver, _trajectory_service, _loitering_service, _response_builder
    
    if _db_manager is None:
        logger.info("Initializing services...")
        
        # Data layer
        _db_manager = DuckDBManager()
        parquet_loader = ParquetLoader()
        parquet_loader.register_with_duckdb(_db_manager.conn, settings.parquet_path, "ais")
        
        # Services
        _memory_manager = MemoryManager(max_history=settings.max_conversation_history)
        _intent_parser = IntentParser()
        _plan_validator = PlanValidator()
        _vessel_resolver = VesselResolver(_db_manager)
        _trajectory_service = TrajectoryService(_db_manager)
        _loitering_service = LoiteringService()
        _response_builder = ResponseBuilder()
        
        logger.info("Services initialized successfully")


# ============================================================================
# LANGGRAPH NODES
# ============================================================================

def resolve_references_node(state: AgentState) -> AgentState:
    """
    Resolve pronoun references in the query.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state
    """
    _initialize_services()
    
    logger.info("Node: resolve_references")
    state["execution_log"].append("Resolving references")
    
    try:
        resolved = _memory_manager.resolve_references(state["user_query"])
        
        if resolved["has_reference"]:
            # Update query context (this will be used by intent parser)
            logger.info(f"Resolved references: {resolved}")
            state["execution_log"].append(f"Resolved references: {resolved}")
        
        return state
        
    except Exception as e:
        logger.error(f"Reference resolution failed: {e}")
        state["error"] = f"Reference resolution failed: {e}"
        return state


def parse_intent_node(state: AgentState) -> AgentState:
    """
    Parse user query using LLM.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with canonical_intent
    """
    _initialize_services()
    
    logger.info("Node: parse_intent")
    state["execution_log"].append("Parsing intent with LLM")
    
    try:
        canonical_intent = _intent_parser.parse(
            state["user_query"],
            state["conversation_history"],
            model_name=state.get("model_name", "llama3")
        )
        
        state["canonical_intent"] = canonical_intent
        state["execution_log"].append(f"Intent: {canonical_intent.domain_intent}/{canonical_intent.task_intent}")
        
        return state
        
    except Exception as e:
        logger.error(f"Intent parsing failed: {e}")
        state["error"] = f"Intent parsing failed: {e}"
        return state


def validate_plan_node(state: AgentState) -> AgentState:
    """
    Validate the parsed intent.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with validation_errors
    """
    _initialize_services()
    
    logger.info("Node: validate_plan")
    state["execution_log"].append("Validating plan")
    
    try:
        errors = _plan_validator.validate(state["canonical_intent"])
        state["validation_errors"] = errors
        
        if errors:
            logger.warning(f"Validation failed: {errors}")
            state["error"] = f"Validation failed: {'; '.join(errors)}"
        else:
            state["execution_log"].append("Plan validated successfully")
        
        return state
        
    except Exception as e:
        logger.error(f"Plan validation failed: {e}")
        state["error"] = f"Plan validation failed: {e}"
        return state


def resolve_vessels_node(state: AgentState) -> AgentState:
    """
    Resolve vessel identifiers to MMSIs.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with vessel_ids
    """
    _initialize_services()
    
    logger.info("Node: resolve_vessels")
    state["execution_log"].append("Resolving vessel identifiers")
    
    try:
        intent = state["canonical_intent"]
        
        # Handle "all" scope
        if intent.vessel_scope == "all":
            vessel_ids = _vessel_resolver.get_all_mmsis()
            logger.info(f"Resolved 'all' to {len(vessel_ids)} vessels")
        else:
            vessel_ids = _vessel_resolver.resolve(intent.vessels)
        
        state["vessel_ids"] = vessel_ids
        state["execution_log"].append(f"Resolved {len(vessel_ids)} vessel(s)")
        
        # Resolve time range
        if intent.time_constraint.mode == "relative":
            start, end = parse_relative_time(intent.time_constraint.relative)
            state["resolved_time_range"] = {"start": start, "end": end}
            state["execution_log"].append(f"Time range: {start} to {end}")
        else:
            start = datetime.fromisoformat(intent.time_constraint.start)
            end = datetime.fromisoformat(intent.time_constraint.end)
            state["resolved_time_range"] = {"start": start, "end": end}
        
        return state
        
    except Exception as e:
        logger.error(f"Vessel resolution failed: {e}")
        state["error"] = f"Vessel resolution failed: {e}"
        return state


def trajectory_pipeline_node(state: AgentState) -> AgentState:
    """
    Fetch trajectory data.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with dataframe
    """
    _initialize_services()
    
    logger.info("Node: trajectory_pipeline")
    state["execution_log"].append("Fetching trajectory data")
    
    try:
        df = _trajectory_service.fetch_raw_trajectory(
            vessel_ids=state["vessel_ids"],
            time_range=state["resolved_time_range"],
            limit=state["canonical_intent"].output.limit
        )
        
        state["dataframe"] = df
        state["execution_log"].append(f"Fetched {len(df)} trajectory points")
        
        return state
        
    except Exception as e:
        logger.error(f"Trajectory fetch failed: {e}")
        state["error"] = f"Trajectory fetch failed: {e}"
        return state


def loitering_pipeline_node(state: AgentState) -> AgentState:
    """
    Detect loitering events.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with dataframe
    """
    _initialize_services()
    
    logger.info("Node: loitering_pipeline")
    state["execution_log"].append("Detecting loitering")
    
    try:
        # First fetch trajectory
        df = _trajectory_service.fetch_raw_trajectory(
            vessel_ids=state["vessel_ids"],
            time_range=state["resolved_time_range"],
            limit=state["canonical_intent"].output.limit * 10  # More data for loitering detection
        )
        
        # Then detect loitering
        loitering_df = _loitering_service.detect_loitering(
            df,
            spatial_constraint=state["canonical_intent"].spatial_constraint
        )
        
        state["dataframe"] = loitering_df
        state["execution_log"].append(f"Detected {len(loitering_df)} loitering events")
        
        return state
        
    except Exception as e:
        logger.error(f"Loitering detection failed: {e}")
        state["error"] = f"Loitering detection failed: {e}"
        return state


def response_builder_node(state: AgentState) -> AgentState:
    """
    Build formatted response.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with result
    """
    _initialize_services()
    
    logger.info("Node: response_builder")
    state["execution_log"].append("Building response")
    
    try:
        response = _response_builder.build_response(
            df=state["dataframe"],
            output_format=state["canonical_intent"].output.format,
            limit=state["canonical_intent"].output.limit
        )
        
        state["result"] = response
        state["execution_log"].append("Response built successfully")
        
        # Update memory
        _memory_manager.add_message("user", state["user_query"])
        _memory_manager.add_message("assistant", response.get("message", ""))
        _memory_manager.update_vessel_context(state["vessel_ids"])
        _memory_manager.update_intent_context(state["canonical_intent"].domain_intent)
        
        return state
        
    except Exception as e:
        logger.error(f"Response building failed: {e}")
        state["error"] = f"Response building failed: {e}"
        return state


# ============================================================================
# CONDITIONAL ROUTING
# ============================================================================

def should_continue_after_validation(state: AgentState) -> str:
    """Determine if we should continue after validation."""
    if state.get("error") or state.get("validation_errors"):
        return "error"
    return "continue"


def route_by_domain(state: AgentState) -> str:
    """Route to appropriate pipeline based on domain intent."""
    domain = state["canonical_intent"].domain_intent
    
    if domain in ["trajectory", "listing"]:
        return "trajectory"
    elif domain == "loitering":
        return "loitering"
    elif domain == "prediction":
        # TODO: Implement prediction pipeline
        return "trajectory"  # Fallback to trajectory for now
    else:
        return "trajectory"


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def create_orchestration_graph() -> StateGraph:
    """
    Create the LangGraph orchestration workflow.
    
    Returns:
        Compiled StateGraph
    """
    logger.info("Creating orchestration graph")
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("resolve_references", resolve_references_node)
    workflow.add_node("parse_intent", parse_intent_node)
    workflow.add_node("validate_plan", validate_plan_node)
    workflow.add_node("resolve_vessels", resolve_vessels_node)
    workflow.add_node("trajectory_pipeline", trajectory_pipeline_node)
    workflow.add_node("loitering_pipeline", loitering_pipeline_node)
    workflow.add_node("response_builder", response_builder_node)
    
    # Set entry point
    workflow.set_entry_point("resolve_references")
    
    # Add edges
    workflow.add_edge("resolve_references", "parse_intent")
    workflow.add_edge("parse_intent", "validate_plan")
    
    # Conditional edge after validation
    workflow.add_conditional_edges(
        "validate_plan",
        should_continue_after_validation,
        {
            "error": END,
            "continue": "resolve_vessels"
        }
    )
    
    # Conditional edge for domain routing
    workflow.add_conditional_edges(
        "resolve_vessels",
        route_by_domain,
        {
            "trajectory": "trajectory_pipeline",
            "loitering": "loitering_pipeline"
        }
    )
    
    # Both pipelines go to response builder
    workflow.add_edge("trajectory_pipeline", "response_builder")
    workflow.add_edge("loitering_pipeline", "response_builder")
    workflow.add_edge("response_builder", END)
    
    logger.info("Graph created successfully")
    return workflow.compile()
