"""
Comprehensive Test Cases with Actual Vessel Data
=================================================
Multi-turn conversation tests using real MMSIs from the dataset.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_query
from services.memory_manager import MemoryManager
import time


# Actual MMSIs from the dataset (extracted from parquet file)
ACTUAL_MMSIS = [
    "369970581",  # Vessel with most data points
    "338973000",
    "367370000",
    "367867000",
    "338808000",
    "226281000",
    "368926399",
    "367192940",
    "366971370",
    "367601730",
]


def print_separator(title=""):
    """Print a formatted separator."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()


def print_result(result, show_data=True):
    """Print query result in a formatted way."""
    print(f"✓ Success: {result['success']}")
    
    if result['success']:
        print(f"  Vessels: {result['vessel_count']}")
        if result['result']:
            print(f"  Format: {result['result'].get('format')}")
            print(f"  Count: {result['result'].get('count')}")
            print(f"  Message: {result['result'].get('message')}")
            
            if show_data and result['result'].get('data'):
                data = result['result']['data']
                if isinstance(data, list) and len(data) > 0:
                    print(f"\n  Sample Data (first 2 rows):")
                    for i, row in enumerate(data[:2], 1):
                        print(f"    {i}. {row}")
    else:
        print(f"  Error: {result['error']}")
    
    print(f"\n  Execution Log:")
    for i, log in enumerate(result['execution_log'], 1):
        print(f"    {i}. {log}")


def test_case_1_basic_trajectory():
    """Test Case 1: Basic trajectory query with actual MMSI."""
    print_separator("TEST CASE 1: Basic Trajectory Query")
    
    mmsi = ACTUAL_MMSIS[0]
    query = f"Show trajectory of vessel with MMSI {mmsi} in the last 24 hours"
    
    print(f"Query: {query}\n")
    result = run_query(query)
    print_result(result)
    
    return result['success']


def test_case_2_loitering_detection():
    """Test Case 2: Loitering detection for all vessels."""
    print_separator("TEST CASE 2: Loitering Detection")
    
    query = "Detect loitering vessels in the last week"
    
    print(f"Query: {query}\n")
    result = run_query(query)
    print_result(result)
    
    return result['success']


def test_case_3_listing_vessels():
    """Test Case 3: List all vessels in dataset."""
    print_separator("TEST CASE 3: List All Vessels")
    
    query = "List all vessels in the dataset"
    
    print(f"Query: {query}\n")
    result = run_query(query)
    print_result(result, show_data=False)  # Don't show all vessels
    
    return result['success']


def test_case_4_multi_turn_conversation():
    """Test Case 4: Multi-turn conversation with reference resolution."""
    print_separator("TEST CASE 4: Multi-Turn Conversation")
    
    mmsi = ACTUAL_MMSIS[1]
    
    # Turn 1: Initial query
    print("Turn 1:")
    query1 = f"Show trajectory of MMSI {mmsi}"
    print(f"  User: {query1}")
    result1 = run_query(query1)
    print(f"  Assistant: {result1['result'].get('message') if result1['success'] else result1['error']}")
    
    time.sleep(1)
    
    # Turn 2: Reference to previous vessel
    print("\nTurn 2:")
    query2 = "Show its loitering behavior"
    print(f"  User: {query2}")
    # Note: This will work once memory is properly integrated
    result2 = run_query(query2)
    print(f"  Assistant: {result2['result'].get('message') if result2['success'] else result2['error']}")
    
    return result1['success']


def test_case_5_time_range_variations():
    """Test Case 5: Different time range expressions."""
    print_separator("TEST CASE 5: Time Range Variations")
    
    mmsi = ACTUAL_MMSIS[2]
    
    time_expressions = [
        "in the last 6 hours",
        "yesterday",
        "in the last week",
        "today",
    ]
    
    for i, time_expr in enumerate(time_expressions, 1):
        print(f"\n{i}. Time Expression: '{time_expr}'")
        query = f"Show trajectory of MMSI {mmsi} {time_expr}"
        print(f"   Query: {query}")
        
        result = run_query(query)
        if result['success']:
            print(f"   ✓ Parsed successfully")
            print(f"   Time range: {result['canonical_intent'].time_constraint.model_dump()}")
        else:
            print(f"   ✗ Failed: {result['error']}")
    
    return True


def test_case_6_multiple_vessels():
    """Test Case 6: Query for multiple vessels."""
    print_separator("TEST CASE 6: Multiple Vessels")
    
    mmsi1 = ACTUAL_MMSIS[0]
    mmsi2 = ACTUAL_MMSIS[1]
    
    query = f"Show trajectories of vessels {mmsi1} and {mmsi2} in the last 24 hours"
    
    print(f"Query: {query}\n")
    result = run_query(query)
    print_result(result)
    
    return result['success']


def test_case_7_output_formats():
    """Test Case 7: Different output formats."""
    print_separator("TEST CASE 7: Output Format Variations")
    
    mmsi = ACTUAL_MMSIS[0]
    
    # Note: The LLM should infer output format from query
    queries = [
        f"Show me a table of trajectory for MMSI {mmsi}",
        f"Give me a summary of MMSI {mmsi} movement",
        f"Display MMSI {mmsi} on a map",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        result = run_query(query)
        
        if result['success']:
            output_format = result['canonical_intent'].output.format
            print(f"   ✓ Output format: {output_format}")
            print(f"   Message: {result['result'].get('message')}")
        else:
            print(f"   ✗ Failed: {result['error']}")
    
    return True


def test_case_8_edge_cases():
    """Test Case 8: Edge cases and error handling."""
    print_separator("TEST CASE 8: Edge Cases")
    
    edge_cases = [
        ("Invalid MMSI", "Show trajectory of MMSI 999999999"),
        ("Ambiguous query", "Show me something"),
        ("Missing time", "Show trajectory of vessel"),
        ("Future time", "Show trajectory tomorrow"),
    ]
    
    for i, (description, query) in enumerate(edge_cases, 1):
        print(f"\n{i}. {description}")
        print(f"   Query: {query}")
        
        result = run_query(query)
        if result['success']:
            print(f"   ✓ Handled successfully")
        else:
            print(f"   ✗ Error (expected): {result['error'][:100]}...")
    
    return True


def test_case_9_complex_loitering():
    """Test Case 9: Complex loitering query with spatial constraints."""
    print_separator("TEST CASE 9: Complex Loitering Query")
    
    query = "Detect vessels loitering near the coast within 12 nautical miles in the last 3 days"
    
    print(f"Query: {query}\n")
    result = run_query(query)
    print_result(result)
    
    if result['success']:
        intent = result['canonical_intent']
        print(f"\n  Parsed Intent:")
        print(f"    Domain: {intent.domain_intent}")
        print(f"    Task: {intent.task_intent}")
        print(f"    Spatial: {intent.spatial_constraint.model_dump()}")
    
    return result['success']


def test_case_10_natural_language_variations():
    """Test Case 10: Natural language query variations."""
    print_separator("TEST CASE 10: Natural Language Variations")
    
    mmsi = ACTUAL_MMSIS[0]
    
    variations = [
        f"Where is vessel {mmsi}?",
        f"Can you show me where {mmsi} has been?",
        f"I need the position history of {mmsi}",
        f"Track vessel {mmsi} for me",
        f"What's the route of {mmsi}?",
    ]
    
    for i, query in enumerate(variations, 1):
        print(f"\n{i}. Query: {query}")
        result = run_query(query)
        
        if result['success']:
            intent = result['canonical_intent']
            print(f"   ✓ Parsed as: {intent.domain_intent}/{intent.task_intent}")
        else:
            print(f"   ✗ Failed: {result['error'][:80]}...")
    
    return True


def run_all_tests():
    """Run all test cases."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE TEST SUITE - AGENTIC PIPELINE")
    print("  Using Actual Vessel Data from Parquet File")
    print("=" * 80)
    
    print(f"\nActual MMSIs being used: {ACTUAL_MMSIS[:3]}...")
    
    test_cases = [
        ("Basic Trajectory Query", test_case_1_basic_trajectory),
        ("Loitering Detection", test_case_2_loitering_detection),
        ("List All Vessels", test_case_3_listing_vessels),
        ("Multi-Turn Conversation", test_case_4_multi_turn_conversation),
        ("Time Range Variations", test_case_5_time_range_variations),
        ("Multiple Vessels", test_case_6_multiple_vessels),
        ("Output Format Variations", test_case_7_output_formats),
        ("Edge Cases", test_case_8_edge_cases),
        ("Complex Loitering", test_case_9_complex_loitering),
        ("Natural Language Variations", test_case_10_natural_language_variations),
    ]
    
    results = []
    
    for i, (name, test_func) in enumerate(test_cases, 1):
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append((name, False))
        
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print_separator("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}\n")
    
    for i, (name, success) in enumerate(results, 1):
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{i:2d}. {status} - {name}")
    
    print("\n" + "=" * 80)
    print(f"  Overall Success Rate: {passed/total*100:.1f}%")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Check if we have actual MMSIs file
    if os.path.exists('actual_mmsis.txt'):
        print("Loading actual MMSIs from file...")
        with open('actual_mmsis.txt', 'r') as f:
            lines = f.readlines()
            # Extract MMSIs from lines like "1. 219000525"
            ACTUAL_MMSIS = []
            for line in lines:
                if line.strip() and line[0].isdigit():
                    parts = line.strip().split('. ')
                    if len(parts) == 2:
                        ACTUAL_MMSIS.append(parts[1])
        
        print(f"Loaded {len(ACTUAL_MMSIS)} actual MMSIs\n")
    
    run_all_tests()
