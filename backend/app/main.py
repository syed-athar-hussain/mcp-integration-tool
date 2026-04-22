from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.mcp.rpc import router as mcp_router
from app.github.webhook import router as github_router
from app.telemetry import instrument_app  # reuse from Project 1 if needed

app = FastAPI(title="MCP GitHub Integration Tool")
instrument_app(app)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(mcp_router, prefix="/mcp")
app.include_router(github_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)