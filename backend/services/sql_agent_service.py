
import os
import duckdb
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env from the same directory as this file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(env_path)

# Path to the parquet file (Time Series Data)
PARQUET_FILE = "/home/crimsondeepdarshak/Desktop/Deep_Darshak/AIS_data_demo/processed/10_Day_US_interpolated_15min.parquet"
# Path to a CSV file for Metadata (Name, CallSign, Type). We just pick one as a reference for static data.
METADATA_CSV = "/home/crimsondeepdarshak/Desktop/Deep_Darshak/AIS_data_demo/ais-2025-01-08.csv"

class MockSQLDatabase(SQLDatabase):
    """
    A custom SQLDatabase that bypasses SQLAlchemy reflection entirely.
    This is needed because duckdb-engine sometimes fails on introspection of views 
    or internal tables (pg_collation), and we simply want to provide a fixed schema.
    """
    def __init__(self, engine):
        self._engine = engine
        self._schema = None
        self._metadata = None
        self.include_tables = ["vessel_data", "vessel_metadata"]
        self.exclude_tables = []
        self._sample_rows_in_table_info = 0
        self._indexes_in_table_info = False
        self._custom_table_info = {}
        self._view_support = True
        # Do NOT call super().__init__ which triggers inspection
        
    def get_table_names(self):
        return ["vessel_data", "vessel_metadata"]
    
    def get_table_info(self, table_names=None):
        prefix = """You are an agent designed to interact with a SQL database (DuckDB).
You have access to two tables:

1. `vessel_data` (Time-series position reports):
- BASEDATETIME (TIMESTAMP)
- MMSI (INTEGER) - Join Key
- LAT (FLOAT)
- LON (FLOAT)
- SOG (FLOAT)
- COG (FLOAT)

2. `vessel_metadata` (Static vessel information):
- mmsi (INTEGER) - Join Key
- vessel_name (VARCHAR)
- call_sign (VARCHAR)
- vessel_type (VARCHAR)
- imo (VARCHAR)
- length (FLOAT)
- width (FLOAT)

GUIDELINES:
- To find vessel names or types, JOIN `vessel_data` with `vessel_metadata` on MMSI.
- `vessel_data` contains historical positions.
- `vessel_metadata` contains the names and types.
- If asked for "unique vessels", select from `vessel_metadata` or `DISTINCT MMSI` from `vessel_data`.

Given an input question, create a syntactically correct DuckDB query to run, then look at the results of the query and return the answer.
"""
        schema_info = """
CREATE TABLE vessel_data (
    BASEDATETIME TIMESTAMP,
    MMSI INTEGER,
    LAT FLOAT,
    LON FLOAT,
    SOG FLOAT,
    COG FLOAT
);

CREATE TABLE vessel_metadata (
    mmsi INTEGER,
    vessel_name VARCHAR,
    call_sign VARCHAR,
    vessel_type VARCHAR,
    imo VARCHAR,
    length FLOAT,
    width FLOAT
);
"""
        return prefix + schema_info
    def run(self, command: str, fetch: str = "all", **kwargs):
        return super().run(command, fetch, **kwargs)

class SQLAgentService:
    def __init__(self):
        self.agent_executor = None
        self.db = None
        self._initialize_agent()

    def _initialize_agent(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY not found. SQL Agent will not be initialized.")
            return

        try:
            # 1. Setup DuckDB with SQLAlchemy
            engine = create_engine("duckdb:///:memory:")
            
            with engine.begin() as conn:
                conn.execute(text(f"CREATE OR REPLACE VIEW vessel_data AS SELECT * FROM read_parquet('{PARQUET_FILE}')"))
                # Create a view for metadata. We distinct by MMSI to get unique vessel info.
                # using read_csv_auto for the CSV
                conn.execute(text(f"CREATE OR REPLACE VIEW vessel_metadata AS SELECT DISTINCT mmsi, vessel_name, call_sign, vessel_type, imo, length, width FROM read_csv_auto('{METADATA_CSV}')"))
            
            # 2. Initialize Custom SQLDatabase
            self.db = MockSQLDatabase(engine)

            # 3. Initialize LLM
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

            # 4. Create Agent
            self.agent_executor = create_sql_agent(
                llm=llm,
                db=self.db,
                agent_type="openai-tools",
                verbose=True,
                handle_parsing_errors=True
            )
            print("SQL Agent initialized successfully.")

        except Exception as e:
            print(f"Error initializing SQL Agent: {e}")
            import traceback
            traceback.print_exc()
            self.agent_executor = None

    def query(self, text: str) -> str:
        if not self.agent_executor:
            return "SQL Agent is not available (check logs for initialization errors or missing API key)."
        
        try:
            # Run the agent
            result = self.agent_executor.invoke(text)
            return result.get("output", "No output returned.")
        except Exception as e:
            print(f"Error executing SQL Agent query: {e}")
            return f"Error processing query: {str(e)}"

# Singleton instance
sql_agent_service = SQLAgentService()
