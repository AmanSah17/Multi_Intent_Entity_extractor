"""
FastAPI WebSocket Server for Agentic Pipeline
==============================================
Real-time communication with the agentic pipeline.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List
import json
import sys
import os

# Add agentic_pipeline to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agentic_pipeline'))

from main import run_query
from services.memory_manager import MemoryManager

app = FastAPI(title="Agentic Pipeline WebSocket API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memory manager for conversation history
memory_manager = MemoryManager(max_history=50)

# Active WebSocket connections
class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

manager = ConnectionManager()


@app.get("/")
async def get_home():
    """Serve the frontend HTML."""
    with open("frontend_ws.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/history")
async def get_history():
    """Get conversation history."""
    return {
        "history": memory_manager.conversation_history,
        "context_summary": memory_manager.get_context_summary()
    }


@app.post("/api/clear")
async def clear_history():
    """Clear conversation history."""
    memory_manager.clear()
    return {"status": "cleared"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time query processing."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive query from client
            data = await websocket.receive_json()
            query = data.get("query", "")
            model = data.get("model", "llama3")
            
            if not query:
                await manager.send_message({
                    "type": "error",
                    "message": "Empty query"
                }, websocket)
                continue
            
            # Send acknowledgment
            await manager.send_message({
                "type": "status",
                "message": f"Processing query with {model}...",
                "query": query
            }, websocket)
            
            try:
                # Run query through agentic pipeline
                result = run_query(
                    query, 
                    memory_manager.conversation_history,
                    model_name=model
                )
                
                # Extract canonical intent
                canonical_intent = None
                if result.get("canonical_intent"):
                    canonical_intent = result["canonical_intent"].model_dump()
                
                # Send canonical intent
                await manager.send_message({
                    "type": "intent",
                    "data": canonical_intent,
                    "message": "Intent parsed"
                }, websocket)
                
                # Send execution log
                await manager.send_message({
                    "type": "log",
                    "data": result.get("execution_log", []),
                    "message": "Execution steps"
                }, websocket)
                
                # Send final result
                await manager.send_message({
                    "type": "result",
                    "success": result.get("success", False),
                    "data": result.get("result"),
                    "error": result.get("error"),
                    "vessel_count": result.get("vessel_count", 0),
                    "message": "Query complete"
                }, websocket)
                
                # Update memory
                memory_manager.add_message("user", query)
                if result.get("success"):
                    response_msg = result.get("result", {}).get("message", "Query processed")
                    memory_manager.add_message("assistant", response_msg)
                    
                    # Update vessel context
                    if result.get("canonical_intent"):
                        vessels = [v.mmsi for v in result["canonical_intent"].vessels if v.mmsi]
                        if vessels:
                            memory_manager.update_vessel_context(vessels)
                
                # Send updated history
                await manager.send_message({
                    "type": "history",
                    "data": memory_manager.conversation_history[-10:],  # Last 10 messages
                    "message": "History updated"
                }, websocket)
                
            except Exception as e:
                await manager.send_message({
                    "type": "error",
                    "message": str(e),
                    "query": query
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
