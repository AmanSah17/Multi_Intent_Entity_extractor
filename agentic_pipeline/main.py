"""
Main Entry Point
================
Main entry point for the agentic orchestration pipeline.
"""

import sys
from typing import List, Dict, Optional
from core.graph import create_orchestration_graph
from core.state import create_initial_state, AgentState
from utils.logger import setup_logger

logger = setup_logger(__name__)


def run_query(
    user_query: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    model_name: str = "llama3"
) -> Dict:
    """
    Execute a user query through the agentic pipeline.
    
    Args:
        user_query: Natural language query from user
        conversation_history: Optional conversation history
        model_name: LLM model to use (llama3, phi3, mistral)
        
    Returns:
        Dictionary with results and execution log
    """
    logger.info(f"Processing query: {user_query} [Model: {model_name}]")
    
    try:
        # Create initial state
        initial_state = create_initial_state(user_query, conversation_history, model_name)
        
        # Create and run graph
        graph = create_orchestration_graph()
        final_state = graph.invoke(initial_state)
        
        # Extract results
        result = {
            "success": final_state.get("error") is None,
            "result": final_state.get("result"),
            "execution_log": final_state.get("execution_log", []),
            "error": final_state.get("error"),
            "canonical_intent": final_state.get("canonical_intent"),
            "vessel_count": len(final_state.get("vessel_ids", [])),
        }
        
        if result["success"]:
            logger.info("Query processed successfully")
        else:
            logger.error(f"Query failed: {result['error']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}", exc_info=True)
        return {
            "success": False,
            "result": None,
            "execution_log": [],
            "error": str(e),
            "canonical_intent": None,
            "vessel_count": 0,
        }


def main():
    """
    Main CLI entry point.
    
    Usage:
        python main.py "Show trajectory of vessel with MMSI 123456789"
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<query>\"")
        print("\nExamples:")
        print("  python main.py \"Show trajectory of MMSI 123456789 in last 6 hours\"")
        print("  python main.py \"Detect loitering vessels in the last week\"")
        print("  python main.py \"List all vessels\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    print("=" * 80)
    print("AGENTIC ORCHESTRATION PIPELINE")
    print("=" * 80)
    print(f"\nQuery: {query}\n")
    
    result = run_query(query)
    
    print("-" * 80)
    print("EXECUTION LOG:")
    print("-" * 80)
    for i, log_entry in enumerate(result["execution_log"], 1):
        print(f"{i}. {log_entry}")
    
    print("\n" + "-" * 80)
    print("RESULT:")
    print("-" * 80)
    
    if result["success"]:
        print(f"Status: SUCCESS")
        print(f"Vessels: {result['vessel_count']}")
        print(f"\nData:")
        
        if result["result"]:
            print(f"  Format: {result['result'].get('format')}")
            print(f"  Count: {result['result'].get('count')}")
            print(f"  Message: {result['result'].get('message')}")
            
            # Print sample data
            if result["result"].get("data"):
                data = result["result"]["data"]
                if isinstance(data, list) and len(data) > 0:
                    print(f"\n  Sample (first 3 rows):")
                    for i, row in enumerate(data[:3], 1):
                        print(f"    {i}. {row}")
                elif isinstance(data, str):
                    print(f"\n  {data}")
    else:
        print(f"Status: FAILED")
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
