from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from .tools import get_repo_files, post_pr_comment
from .rag import build_repo_rag_context
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next: str

llm_openai = ChatOpenAI(model="gpt-4o", temperature=0)
llm_claude = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)

tools = [get_repo_files, post_pr_comment]
tool_node = ToolNode(tools)

SYSTEM_PROMPT = SystemMessage(content="""You are a senior code reviewer. 
Use MCP tools to fetch repo files and post PR comments. 
Always use RAG context from get_repo_files before reviewing.""")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def claude_review_node(state: AgentState):
    rag_context = await build_repo_rag_context(state["messages"][-1].content)  # last message has files
    messages = [SYSTEM_PROMPT] + state["messages"] + [HumanMessage(content=f"Repo context:\n{rag_context}\n\nReview this PR.")]
    response = await llm_claude.ainvoke(messages)
    return {"messages": [response], "next": "tools"}

def supervisor_node(state: AgentState):
    return {"next": "claude"}  # always route to Claude for reviews

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("claude", claude_review_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", lambda x: x["next"])
workflow.add_edge("claude", "tools")
workflow.add_edge("tools", END)

graph = workflow.compile()

async def run_mcp_github_review(pr_url: str, repo: str) -> dict:
    """Main entrypoint – called by webhook"""
    initial_state = {
        "messages": [HumanMessage(content=f"PR: {pr_url} | Repo: {repo}")]
    }
    result = await graph.ainvoke(initial_state)
    final_comment = result["messages"][-1].content
    return {"review_comment": final_comment, "pr_url": pr_url}