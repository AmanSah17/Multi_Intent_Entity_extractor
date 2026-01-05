
import os
import sys

# Ensure backend directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from services.sql_agent_service import sql_agent_service

def test_agent():
    print("Testing SQL Agent Service...")
    
    # Check if key exists
    if not os.getenv("OPENAI_API_KEY"):
        print("NOTICE: OPENAI_API_KEY is not set. The agent will likely return a warning message.")
    
    query = "show all unique vessels (NAME and corresponding MMSI, Vessel Type, CallSign), moving above 20 Nautical Miles speed over ground at any instant of time."
    print(f"\nQuery: {query}")
    result = sql_agent_service.query(query)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_agent()
