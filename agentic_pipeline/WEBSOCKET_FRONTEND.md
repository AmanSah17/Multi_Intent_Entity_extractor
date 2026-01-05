# WebSocket Frontend - Quick Start

## Start the WebSocket Server

```bash
cd agentic_pipeline
python api_server.py
```

Server will start on: **http://localhost:8001**

## Access the Frontend

Open in browser: **http://localhost:8001**

## Features

### 1. Real-Time Chat Interface
- Send queries and get instant responses
- Beautiful gradient UI with animations
- Auto-scrolling message history

### 2. JSON Intent Display
- See the parsed canonical intent in real-time
- Formatted JSON with syntax highlighting
- Updates with each query

### 3. Conversation History
- View all past messages
- User and assistant messages separated
- Clear history button

### 4. Execution Logs
- See each step of the pipeline
- Real-time log updates
- Step-by-step execution tracking

### 5. Example Queries
- Click to auto-fill query input
- Pre-configured working examples
- Quick testing

## Example Usage

1. **Start Server:**
   ```bash
   python api_server.py
   ```

2. **Open Browser:**
   - Go to http://localhost:8001

3. **Try Example Queries:**
   - Click any example query button
   - Or type your own query
   - Press Enter or click Send

4. **View Results:**
   - See response in chat
   - Check Intent JSON tab for parsed intent
   - View Logs tab for execution steps
   - Check History tab for conversation

## API Endpoints

- `GET /` - Serve frontend HTML
- `GET /api/history` - Get conversation history
- `POST /api/clear` - Clear conversation history
- `WS /ws` - WebSocket connection for real-time queries

## WebSocket Message Types

### Client → Server
```json
{
  "query": "Show trajectory of MMSI 369970581"
}
```

### Server → Client

**Status:**
```json
{
  "type": "status",
  "message": "Processing query...",
  "query": "..."
}
```

**Intent:**
```json
{
  "type": "intent",
  "data": { /* canonical intent JSON */ },
  "message": "Intent parsed"
}
```

**Logs:**
```json
{
  "type": "log",
  "data": ["Step 1", "Step 2", ...],
  "message": "Execution steps"
}
```

**Result:**
```json
{
  "type": "result",
  "success": true,
  "data": { /* query results */ },
  "vessel_count": 1,
  "message": "Query complete"
}
```

**History:**
```json
{
  "type": "history",
  "data": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "message": "History updated"
}
```

## Troubleshooting

### WebSocket Connection Failed
- Make sure `api_server.py` is running
- Check port 8001 is not in use
- Try refreshing the browser

### No Response
- Check backend logs in terminal
- Verify OpenAI API key is set
- Check parquet file path in settings

### CORS Errors
- Server has CORS enabled for all origins
- If issues persist, check browser console

## Next Steps

1. **Customize UI:**
   - Edit `frontend_ws.html`
   - Change colors, layout, etc.

2. **Add Features:**
   - Map visualization
   - Data export
   - Advanced filters

3. **Deploy:**
   - Use production ASGI server (gunicorn + uvicorn)
   - Add authentication
   - Use HTTPS
