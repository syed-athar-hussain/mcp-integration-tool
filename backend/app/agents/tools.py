import httpx
from langchain_core.tools import tool
from app.config import settings

MCP_URL = f"{settings.backend_url}/jsonrpc"

@tool
async def get_repo_files(repo: str, path: str = ".", ref: str = "main") -> str:
    """MCP Client: Calls get_repo_files tool via JSON-RPC"""
    async with httpx.AsyncClient() as client:
        payload = {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {"name": "get_repo_files", "args": {"repo": repo, "path": path, "ref": ref}},
            "id": str(uuid.uuid4())
        }
        resp = await client.post(MCP_URL, json=payload)
        resp.raise_for_status()
        result = resp.json()["result"]
        return json.dumps(result)

@tool
async def post_pr_comment(pr_url: str, comment: str) -> str:
    """MCP Client: Calls post_pr_comment tool via JSON-RPC"""
    async with httpx.AsyncClient() as client:
        payload = {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {"name": "post_pr_comment", "args": {"pr_url": pr_url, "comment": comment}},
            "id": str(uuid.uuid4())
        }
        resp = await client.post(MCP_URL, json=payload)
        resp.raise_for_status()
        return json.dumps(resp.json()["result"])