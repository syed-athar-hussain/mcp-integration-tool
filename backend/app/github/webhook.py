from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
from app.config import settings
from app.agents.graph import run_mcp_github_review

router = APIRouter()

@router.post("/webhook/github")
async def github_pr_webhook(request: Request):
    # Verify webhook signature
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(401, "Missing signature")

    body = await request.body()
    expected = "sha256=" + hmac.new(settings.github_webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(401, "Invalid signature")

    payload = await request.json()
    if payload.get("action") != "opened" or "pull_request" not in payload:
        return {"status": "ignored"}

    pr_url = payload["pull_request"]["html_url"]
    repo = payload["repository"]["full_name"]

    # Trigger LangGraph MCP Client pipeline
    result = await run_mcp_github_review(pr_url, repo)

    return {"status": "review_posted", "comment": result["review_comment"]}