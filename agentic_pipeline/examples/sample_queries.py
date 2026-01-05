"""
Sample Queries Example
======================
Test the agentic pipeline with various query types.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_query


def test_sample_queries():
    """Test various query types."""
    
    queries = [
        # Trajectory queries
        "Show trajectory of vessel with MMSI 123456789 in the last 6 hours",
        "Display the path of MMSI 987654321 yesterday",
        
        # Loitering queries
        "Detect loitering vessels in the last week",
        "Find vessels that stayed in one place for more than 4 hours",
        
        # Listing queries
        "List all vessels",
        "Show all vessels in the dataset",
    ]
    
    print("=" * 80)
    print("TESTING SAMPLE QUERIES")
    print("=" * 80)
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}/{len(queries)}: {query}")
        print("=" * 80)
        
        result = run_query(query)
        
        print("\nExecution Log:")
        for j, log in enumerate(result["execution_log"], 1):
            print(f"  {j}. {log}")
        
        print(f"\nSuccess: {result['success']}")
        
        if result["success"]:
            print(f"Vessels: {result['vessel_count']}")
            if result["result"]:
                print(f"Format: {result['result'].get('format')}")
                print(f"Count: {result['result'].get('count')}")
                print(f"Message: {result['result'].get('message')}")
        else:
            print(f"Error: {result['error']}")
        
        print()


if __name__ == "__main__":
    test_sample_queries()
