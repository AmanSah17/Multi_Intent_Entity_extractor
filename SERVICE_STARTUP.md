# Service Startup Guide

## Agentic Pipeline (New System)

### Quick Start

1. **Install Dependencies:**
   ```bash
   cd agentic_pipeline
   pip install -r requirements.txt
   ```

2. **Test with Sample Query:**
   ```bash
   python main.py "List all vessels"
   ```

3. **Run Example Queries:**
   ```bash
   python examples/sample_queries.py
   ```

## Backend Service (Existing System)

### Start Backend API

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Access at: http://localhost:8000

### API Endpoints

- `POST /nlp/predict` - Intent and entity extraction
- Swagger docs: http://localhost:8000/docs

## Frontend Service (If Available)

```bash
cd frontend
# Check for package.json or requirements
npm install  # or pip install -r requirements.txt
npm run dev  # or python app.py
```

## Running Both Systems

### Terminal 1: Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Terminal 2: Agentic Pipeline Test
```bash
cd agentic_pipeline
python main.py "Show trajectory of MMSI 123456789 in last 6 hours"
```

## Notes

- The **agentic pipeline** is a standalone system (no server required)
- The **backend** is the existing FastAPI service
- Both can run independently
