import json
import uuid
from fastapi import APIRouter, Request, HTTPException
from redis.asyncio import Redis
from app.config import settings
from app.models import JsonRpcRequest, JsonRpcResponse

router = APIRouter()
redis = Redis.from_url(settings.redis_url, decode_responses=True)

TOOLS = {
    "get_repo_files": {
        "name": "get_repo_files",
        "description": "Fetch repository files and content for a given repo and path",
        "parameters": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "owner/repo"},
                "path": {"type": "string", "description": "file or directory path"},
                "ref": {"type": "string", "description": "branch or commit SHA", "default": "main"}
            },
            "required": ["repo", "path"]
        }
    },
    "post_pr_comment": {
        "name": "post_pr_comment",
        "description": "Post a review comment on a GitHub PR",
        "parameters": {
            "type": "object",
            "properties": {
                "pr_url": {"type": "string"},
                "comment": {"type": "string"}
            },
            "required": ["pr_url", "comment"]
        }
    }
}

async def call_tool(method: str, params: Dict):
    """MCP tool execution with Redis context sharing"""
    tool_id = str(uuid.uuid4())
    if method == "get_repo_files":
        return {
            "files": [
                {"path": params.get("path", "README.md"), "content": "# Sample repo content fetched via MCP"}
            ],
            "context_id": tool_id
        }
    elif method == "post_pr_comment":
        return {"status": "comment_posted", "pr_url": params["pr_url"], "context_id": tool_id}
    raise ValueError("Unknown tool")

@router.post("/jsonrpc")
async def jsonrpc_handler(request: Request):
    try:
        body = await request.json()
        req = JsonRpcRequest.model_validate(body)

        if req.method == "list_tools":
            return JsonRpcResponse(jsonrpc="2.0", result=list(TOOLS.values()), id=req.id)

        if req.method == "call_tool":
            tool_name = req.params["name"]
            tool_args = req.params["args"]
            result = await call_tool(tool_name, tool_args)
            # Store result in Redis for shared MCP context across agents
            await redis.set(f"mcp:context:{tool_name}:{req.id}", json.dumps(result), ex=3600)
            return JsonRpcResponse(jsonrpc="2.0", result=result, id=req.id)

        raise HTTPException(400, "Method not found")
    except Exception as e:
        return JsonRpcResponse(
            jsonrpc="2.0",
            error={"code": -32603, "message": str(e)},
            id=req.id if "req" in locals() else None
        )