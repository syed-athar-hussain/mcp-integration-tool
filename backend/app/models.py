from pydantic import BaseModel
from typing import Literal, Dict, Any, List, Optional
from datetime import datetime

class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    method: str
    params: Dict[str, Any]
    id: Optional[str | int | None] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: Literal["2.0"]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str | int | None] = None