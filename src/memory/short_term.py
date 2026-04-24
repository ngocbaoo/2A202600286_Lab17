from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.memory.base import BaseMemory

class ShortTermMemory(BaseMemory):
    """
    Manages the current conversation buffer.
    In LangGraph, this is often integrated into the state, 
    but we provide a wrapper here for consistency.
    """
    def __init__(self):
        self.buffer: List[BaseMessage] = []

    def store(self, key: str, value: Any, metadata: Dict = None):
        if isinstance(value, BaseMessage):
            self.buffer.append(value)
        elif isinstance(value, dict) and "role" in value and "content" in value:
            if value["role"] == "user":
                self.buffer.append(HumanMessage(content=value["content"]))
            else:
                self.buffer.append(AIMessage(content=value["content"]))

    def retrieve(self, query: str, limit: int = 10) -> List[Dict]:
        # Return last N messages
        messages = self.buffer[-limit:]
        return [{"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content} for m in messages]

    def clear(self):
        self.buffer = []
