
from typing import Dict, Set, Any, List
from .schemas import EntityContext, InvestigationResult

class InvestigationState:
    """
    Manages the state of a single investigation session.
    Tracks entities, results of each step, and completion status.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        # The current resolved context (entities)
        self.context: EntityContext = EntityContext()
        # Results keyed by intent name
        self.results: Dict[str, InvestigationResult] = {}
        # Set of completed intents to avoid cycles/re-execution
        self.completed_intents: Set[str] = set()
        # Execution log for debugging
        self.execution_log: List[str] = []

    def update_context(self, new_context: EntityContext):
        """Update the entity context with new findings."""
        # Simple merge strategy: overwrite if provided, append lists
        if new_context.region:
            self.context.region = new_context.region
        if new_context.time_range:
            self.context.time_range = new_context.time_range
        
        # Merge lists uniquely
        self.context.mmsi = list(set(self.context.mmsi + new_context.mmsi))
        self.context.imo = list(set(self.context.imo + new_context.imo))
        self.context.vessel_name = list(set(self.context.vessel_name + new_context.vessel_name))
        
        if new_context.derived_entities:
            self.context.derived_entities.update(new_context.derived_entities)

    def add_result(self, intent: str, result: InvestigationResult):
        """Store the result of an intent execution."""
        self.results[intent] = result
        self.completed_intents.add(intent)
        self.execution_log.append(f"Completed {intent} at {result.timestamp}")

    def get_context_summary(self) -> str:
        """Returns a string summary of the current context for the LLM."""
        return self.context.model_dump_json()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for storage."""
        return {
            "session_id": self.session_id,
            "context": self.context.model_dump(),
            "results": {k: v.model_dump() for k, v in self.results.items()},
            "completed_intents": list(self.completed_intents),
            "execution_log": self.execution_log
        }
