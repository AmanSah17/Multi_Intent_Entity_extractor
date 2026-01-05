from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import nlp

app = FastAPI(title="Intent Service API", version="1.0")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nlp.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
