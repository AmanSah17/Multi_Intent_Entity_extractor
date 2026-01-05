"""
Plan Validator
==============
Schema and logic validation for parsed intents.
"""

from typing import List
from config.schemas import CanonicalIntent
from utils.validators import validate_mmsi, validate_time_range
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PlanValidator:
    """
    Validates parsed intents for schema compliance and logical consistency.
    
    This class ensures that:
    1. Schema is valid (handled by Pydantic)
    2. Business logic is sound
    3. No unsafe operations are requested
    """
    
    def __init__(self):
        """Initialize the plan validator."""
        pass
    
    def validate(self, intent: CanonicalIntent) -> List[str]:
        """
        Validate a canonical intent.
        
        Args:
            intent: CanonicalIntent object to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Schema validation (already done by Pydantic)
        # Now validate business logic
        
        # 1. Validate vessel scope consistency
        if intent.vessel_scope == "single" and len(intent.vessels) != 1:
            errors.append("vessel_scope is 'single' but vessels list does not contain exactly 1 vessel")
        
        if intent.vessel_scope == "multiple" and len(intent.vessels) < 2:
            errors.append("vessel_scope is 'multiple' but vessels list contains less than 2 vessels")
        
        if intent.vessel_scope == "all" and len(intent.vessels) > 0:
            errors.append("vessel_scope is 'all' but vessels list is not empty")
        
        # 2. Validate MMSI format
        for vessel in intent.vessels:
            if vessel.mmsi and not validate_mmsi(vessel.mmsi):
                errors.append(f"Invalid MMSI format: {vessel.mmsi}")
        
        # 3. Validate time constraints
        if intent.time_constraint.mode == "relative":
            if not intent.time_constraint.relative:
                errors.append("Time mode is 'relative' but no relative expression provided")
        
        if intent.time_constraint.mode == "absolute":
            if not intent.time_constraint.start or not intent.time_constraint.end:
                errors.append("Time mode is 'absolute' but start/end not provided")
            elif not validate_time_range(intent.time_constraint.start, intent.time_constraint.end):
                errors.append("Invalid time range: start must be before end")
        
        # 4. Validate spatial constraints
        if intent.spatial_constraint.type == "coastal_distance":
            if intent.spatial_constraint.distance_nm is None or intent.spatial_constraint.distance_nm <= 0:
                errors.append("Spatial type is 'coastal_distance' but distance_nm is invalid")
        
        if intent.spatial_constraint.type == "polygon":
            if not intent.spatial_constraint.polygon_type:
                errors.append("Spatial type is 'polygon' but polygon_type not provided")
        
        # 5. Validate execution mode
        if intent.execution_mode.data_source == "model_inference":
            if not intent.execution_mode.model_name:
                errors.append("Execution mode is 'model_inference' but model_name not provided")
        
        # 6. Validate domain/task intent compatibility
        if intent.domain_intent == "loitering" and intent.task_intent not in ["detect", "show"]:
            errors.append(f"Incompatible: domain_intent 'loitering' with task_intent '{intent.task_intent}'")
        
        if intent.domain_intent == "prediction" and intent.task_intent != "predict":
            errors.append(f"Incompatible: domain_intent 'prediction' with task_intent '{intent.task_intent}'")
        
        # 7. Safety checks
        # Ensure no code execution attempts (this is paranoid but important)
        query_str = str(intent.to_dict())
        unsafe_keywords = ["exec", "eval", "import", "os.", "subprocess", "__"]
        for keyword in unsafe_keywords:
            if keyword in query_str:
                errors.append(f"Unsafe keyword detected: {keyword}")
        
        if errors:
            logger.warning(f"Validation failed with {len(errors)} errors")
            for error in errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("Validation passed")
        
        return errors
    
    def is_valid(self, intent: CanonicalIntent) -> bool:
        """
        Check if intent is valid.
        
        Args:
            intent: CanonicalIntent object
            
        Returns:
            True if valid, False otherwise
        """
        errors = self.validate(intent)
        return len(errors) == 0
