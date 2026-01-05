# Agentic Orchestration Pipeline for Maritime AIS Intelligence

A production-ready, modular agentic pipeline for maritime AIS analytics using LangGraph, DuckDB, and ML models.

## Overview

This system provides:
- **Multi-level intent understanding** (trajectory, loitering, prediction, listing)
- **Entity resolution** across conversation context
- **Safe orchestration** of database queries, geospatial tools, and ML models
- **Deterministic execution** with LLMs used strictly as planners

## Architecture

```
User Query → LangGraph Orchestration
    ├── Reference Resolution
    ├── Intent Parsing (LLM)
    ├── Plan Validation
    ├── Vessel Resolution
    ├── Domain Router
    │   ├── Trajectory Pipeline
    │   └── Loitering Pipeline
    └── Response Builder
```

## Installation

1. **Install dependencies:**
   ```bash
   cd agentic_pipeline
   pip install -r requirements.txt
   ```

2. **Configure settings:**
   - OpenAI API key is already configured in `config/settings.py`
   - Parquet file path is set to your AIS data file
   - Adjust other settings as needed

## Usage

### Command Line

```bash
# Trajectory query
python main.py "Show trajectory of vessel with MMSI 123456789 in the last 6 hours"

# Loitering detection
python main.py "Detect loitering vessels in the last week"

# List all vessels
python main.py "List all vessels"
```

### Python API

```python
from main import run_query

# Execute a query
result = run_query("Show trajectory of MMSI 123456789 in last 6 hours")

# Check results
if result["success"]:
    print(f"Found {result['result']['count']} results")
    print(result["result"]["data"])
else:
    print(f"Error: {result['error']}")
```

### Example Queries

```python
# Run sample queries
python examples/sample_queries.py
```

## Project Structure

```
agentic_pipeline/
├── config/
│   ├── settings.py          # Configuration management
│   └── schemas.py            # Canonical intent & entity schemas
├── core/
│   ├── state.py              # AgentState definition
│   └── graph.py              # LangGraph orchestration
├── services/
│   ├── memory_manager.py     # Conversation history & reference resolution
│   ├── intent_parser.py      # LLM-based structured extraction
│   ├── plan_validator.py     # Schema and logic validation
│   ├── vessel_resolver.py    # IMO/MMSI/name to vessel_id mapping
│   ├── trajectory_service.py # Trajectory handling
│   ├── loitering_service.py  # Loitering detection
│   └── response_builder.py   # Output formatting
├── data/
│   ├── duckdb_manager.py     # DuckDB connection & query execution
│   └── parquet_loader.py     # Parquet data loading
├── utils/
│   ├── logger.py             # Logging utilities
│   └── validators.py         # Data validation helpers
├── examples/
│   └── sample_queries.py     # Example usage
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Key Features

### 1. Canonical Intent Schema

All LLM outputs are validated against a strict Pydantic schema:

```python
{
  "domain_intent": "trajectory | loitering | prediction | listing",
  "task_intent": "show | predict | detect | list",
  "vessel_scope": "single | multiple | all",
  "vessels": [...],
  "time_constraint": {...},
  "spatial_constraint": {...},
  "execution_mode": {...},
  "output": {...}
}
```

### 2. Safety & Determinism

- ✅ LLMs never execute code (only plan)
- ✅ All outputs are schema-validated
- ✅ Deterministic, explainable pipelines
- ✅ SQL injection prevention
- ✅ Safety keyword detection

### 3. Loitering Detection

Detects vessels that:
- Move slowly (< 2 knots by default)
- Stay in one area for extended periods (> 4 hours by default)
- Can be filtered by spatial constraints

### 4. Conversation Context

Resolves references like:
- "Show its trajectory" → resolves "its" to last mentioned vessel
- "Detect loitering for them" → resolves "them" to multiple vessels

## Data Schema

The pipeline works with AIS parquet files containing:
- `BaseDateTime`: Timestamp
- `LAT`: Latitude
- `LON`: Longitude
- `MMSI`: Maritime Mobile Service Identity
- `SOG`: Speed Over Ground
- `COG`: Course Over Ground
- `interpolated`: Interpolation flag

## Configuration

Edit `config/settings.py` to customize:

```python
# LLM Configuration
model_name = "gpt-4o-mini"
temperature = 0.0  # Deterministic

# Loitering Parameters
loitering_speed_threshold_knots = 2.0
loitering_dwell_time_hours = 4.0

# Output
default_result_limit = 50
```

## Examples

### Trajectory Query
```
Query: "Show trajectory of vessel with MMSI 123456789 in the last 6 hours"

Execution Log:
1. Resolving references
2. Parsing intent with LLM
3. Intent: trajectory/show
4. Validating plan
5. Plan validated successfully
6. Resolving vessel identifiers
7. Resolved 1 vessel(s)
8. Fetching trajectory data
9. Fetched 48 trajectory points
10. Building response

Result: Found 48 trajectory points
```

### Loitering Detection
```
Query: "Detect loitering vessels in the last week"

Execution Log:
1. Resolving references
2. Parsing intent with LLM
3. Intent: loitering/detect
4. Validating plan
5. Resolving vessel identifiers
6. Resolved 15 vessel(s)
7. Detecting loitering
8. Detected 3 loitering events

Result: Found 3 loitering events
```

## Future Extensions

- Dark vessel detection (AIS gaps)
- Rendezvous detection (vessel proximity)
- Fleet risk scoring
- Continuous alerting agents
- Model auto-selection
- Vector similarity for behavior patterns
- Kafka integration for streaming
- Apache Iceberg for long-term storage

## Design Principles

1. **LLMs as Planners, Not Executors**: LLMs only parse intent, never execute code
2. **Schema Validation**: All outputs validated with Pydantic
3. **Deterministic Pipelines**: Clear, explainable execution flow
4. **Modular Architecture**: Each component is independent and reusable
5. **Maritime-Domain Optimized**: Specialized for AIS data and vessel analytics

## Troubleshooting

### Import Errors
Make sure you're in the `agentic_pipeline` directory and have installed all dependencies.

### OpenAI API Errors
Check that your API key is valid in `config/settings.py`.

### No Data Found
Verify that:
1. The parquet file path is correct in `config/settings.py`
2. The MMSI exists in your dataset
3. The time range contains data

## License

MIT License

## Author

Maritime Intelligence Team
Version: 1.0.0
