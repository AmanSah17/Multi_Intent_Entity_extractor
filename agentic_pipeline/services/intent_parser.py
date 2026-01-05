"""
Intent Parser
=============
LLM-based structured intent extraction with schema validation.
Uses local Ollama LLM instead of OpenAI.
"""

import json
from typing import List, Dict
# from langchain_openai import ChatOpenAI  # Commented out - using local LLM instead
from langchain_community.llms import Ollama
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import settings
from config.schemas import CanonicalIntent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class IntentParser:
    """
    LLM-based intent parser with structured output.
    
    This class uses a local LLM (Ollama) to parse natural language queries into
    the canonical intent schema. The LLM is used ONLY as a planner,
    not as an executor.
    """
    
    def __init__(self):
        """Initialize the intent parser with local Ollama LLM."""
        # Using Ollama with llama3 model (local, no API key needed)
        self.llm = Ollama(
            model="llama3",  # or "llama2", "mistral", "phi3" - whatever you have installed
            temperature=0.0  # Deterministic
        )
        logger.info(f"Intent parser initialized with local Ollama model: llama3")
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for intent parsing.
        
        Returns:
            System prompt string
        """
        return """You are a maritime AIS query intent parser. Your job is to parse natural language queries into a structured JSON format.

CRITICAL RULES:
1. You MUST output ONLY valid JSON matching the schema below
2. You are a PLANNER, not an executor - never execute code or queries
3. All outputs must be schema-validated
4. Be deterministic and consistent

CANONICAL INTENT SCHEMA:
{
  "domain_intent": "trajectory | loitering | prediction | listing",
  "task_intent": "show | predict | detect | list",
  "vessel_scope": "single | multiple | all",
  "vessels": [
    {"imo": null, "mmsi": "123456789", "name": null}
  ],
  "time_constraint": {
    "mode": "relative | absolute",
    "relative": "last_6h | last_24h | last_week | today | yesterday",
    "start": null,
    "end": null
  },
  "spatial_constraint": {
    "type": "none | coastal_distance | polygon",
    "distance_nm": null,
    "polygon_type": null,
    "polygon_id": null
  },
  "execution_mode": {
    "data_source": "raw_ais | ml_predictions | model_inference",
    "model_name": null
  },
  "output": {
    "format": "map | table | summary",
    "limit": 50
  }
}

DOMAIN INTENT MAPPING:
- "trajectory": Queries about vessel paths, positions, routes
- "loitering": Queries about vessels staying in one area
- "prediction": Queries about future positions
- "listing": Queries to list vessels

TASK INTENT MAPPING:
- "show": Display/retrieve existing data
- "predict": Forecast future states
- "detect": Identify patterns or anomalies
- "list": Enumerate vessels

TIME EXPRESSIONS:
- "last 6 hours" → {"mode": "relative", "relative": "last_6h"}
- "yesterday" → {"mode": "relative", "relative": "yesterday"}
- "between Jan 5 and Jan 12" → {"mode": "absolute", "start": "2020-01-05T00:00:00", "end": "2020-01-12T23:59:59"}

EXAMPLES:

Query: "Show trajectory of vessel with MMSI 123456789 in the last 6 hours"
Output:
{
  "domain_intent": "trajectory",
  "task_intent": "show",
  "vessel_scope": "single",
  "vessels": [{"imo": null, "mmsi": "123456789", "name": null}],
  "time_constraint": {"mode": "relative", "relative": "last_6h", "start": null, "end": null},
  "spatial_constraint": {"type": "none", "distance_nm": null, "polygon_type": null, "polygon_id": null},
  "execution_mode": {"data_source": "raw_ais", "model_name": null},
  "output": {"format": "table", "limit": 50}
}

Query: "Detect loitering vessels near the coast in the last week"
Output:
{
  "domain_intent": "loitering",
  "task_intent": "detect",
  "vessel_scope": "all",
  "vessels": [],
  "time_constraint": {"mode": "relative", "relative": "last_week", "start": null, "end": null},
  "spatial_constraint": {"type": "coastal_distance", "distance_nm": 12.0, "polygon_type": null, "polygon_id": null},
  "execution_mode": {"data_source": "raw_ais", "model_name": null},
  "output": {"format": "table", "limit": 50}
}

Now parse the user's query into this exact JSON format. Output ONLY the JSON, no other text."""
    
    def parse(self, query: str, context: List[Dict[str, str]] = None, model_name: str = "llama3") -> CanonicalIntent:
        """
        Parse user query into canonical intent schema.
        
        Args:
            query: User query string
            context: Optional conversation context
            model_name: Name of the LLM model to use
            
        Returns:
            CanonicalIntent object
            
        Raises:
            ValueError: If parsing fails or schema validation fails
        """
        logger.info(f"Parsing query: {query} using model: {model_name}")
        
        try:
            # Initialize LLM with selected model
            # We create a new instance here to support dynamic switching
            # This is lightweight for Ollama as it just sets the API endpoint parameters
            llm = Ollama(
                model=model_name,
                temperature=0.0
            )
            
            # Build prompt (Ollama uses string prompts, not message objects)
            full_prompt = self._build_system_prompt() + f"\n\nQuery: {query}"
            
            # Call local LLM
            response_text = llm.invoke(full_prompt)
            response_text = response_text.strip()
            
            logger.debug(f"LLM response: {response_text}")
            
            # Check if response is empty
            if not response_text:
                raise ValueError("LLM returned empty response")
            
            # Extract JSON from response (in case LLM adds extra text)
            # Find the first { and last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                logger.error(f"No JSON found in response: {response_text}")
                raise ValueError("No JSON found in LLM response")
            
            json_str = response_text[start_idx:end_idx+1]
            
            # Parse JSON
            intent_dict = json.loads(json_str)
            
            # Check if intent_dict is None or empty
            if not intent_dict:
                raise ValueError("Parsed intent is empty")
            
            # Validate with Pydantic
            canonical_intent = CanonicalIntent(**intent_dict)
            
            logger.info(f"Successfully parsed intent: {canonical_intent.domain_intent}/{canonical_intent.task_intent}")
            return canonical_intent
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        
        except Exception as e:
            logger.error(f"Intent parsing failed: {e}")
            raise ValueError(f"Intent parsing error: {str(e)}")
