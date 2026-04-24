from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from src.memory.short_term import ShortTermMemory
from src.memory.long_term_redis import LongTermRedisMemory
from src.memory.episodic_json import EpisodicJSONMemory
from src.memory.semantic_chroma import SemanticChromaMemory
from src.agent.router import MemoryRouter
from src.agent.context_manager import ContextManager

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The conversation history"]
    memories: List[str]
    routing: Dict[str, Any]
    user_query: str
    user_id: str

class MultiMemoryAgent:
    def __init__(self, model_config: Dict[str, Any], memory_config: Dict[str, Any]):
        print("Initializing MultiMemoryAgent...")
        self.llm = ChatOpenAI(
            api_key=model_config["api_key"],
            base_url=model_config["base_url"],
            model=model_config["model_name"],
            max_retries=10
        )
        
        print("Initializing Router...")
        self.router = MemoryRouter(self.llm)
        print("Initializing Context Manager...")
        self.context_manager = ContextManager(model_name=model_config["model_name"])
        
        # Initialize Memory Backends
        print("Initializing Redis Memory...")
        self.redis_mem = LongTermRedisMemory(
            host=memory_config.get("redis_host", "localhost"),
            port=memory_config.get("redis_port", 6379)
        )
        print("Initializing Episodic Memory...")
        self.episodic_mem = EpisodicJSONMemory(memory_config["episodic_path"])
        print("Initializing Semantic Memory...")
        self.semantic_mem = SemanticChromaMemory(
            path=memory_config["chroma_path"],
            api_key=model_config["api_key"]
        )
        
        print("Building Graph...")
        self.graph = self._build_graph()
        print("MultiMemoryAgent ready.")

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("router", self._route_node)
        workflow.add_node("recall", self._recall_node)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("save", self._save_node)
        
        workflow.set_entry_point("router")
        workflow.add_edge("router", "recall")
        workflow.add_edge("recall", "agent")
        workflow.add_edge("agent", "save")
        workflow.add_edge("save", END)
        
        return workflow.compile(checkpointer=MemorySaver())

    def _route_node(self, state: AgentState):
        query = state["messages"][-1].content
        routing = self.router.route(query)
        return {"routing": routing.dict(), "user_query": query}

    def _recall_node(self, state: AgentState):
        routing = state["routing"]
        query = state["user_query"]
        user_id = state.get("user_id", "default_user")
        
        recalled = []
        
        if routing.get("use_long_term"):
            # Mock preference lookup
            res = self.redis_mem.retrieve(user_id)
            for r in res:
                recalled.append(f"[User Preference] {r['value']}")
        
        if routing.get("use_semantic"):
            res = self.semantic_mem.retrieve(query)
            for r in res:
                recalled.append(f"[Factual Recall] {r['content']}")
                
        if routing.get("use_episodic"):
            res = self.episodic_mem.retrieve(query)
            for r in res:
                recalled.append(f"[Experience Recall] {r['content']}")
                
        return {"memories": recalled}

    def _agent_node(self, state: AgentState):
        system_prompt = "You are a helpful assistant with a multi-memory stack. Use the provided context to answer accurately."
        
        print("Managing context...")
        # Managed context (hierarchy + trimming)
        messages = self.context_manager.manage(
            system_message=system_prompt,
            user_query=state["user_query"],
            recalled_memories=state["memories"],
            history=state["messages"][:-1] # Exclude the current query which is added by context_manager
        )
        
        print("Invoking LLM...")
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    def _save_node(self, state: AgentState):
        query = state["user_query"]
        response = state["messages"][-1].content
        user_id = state.get("user_id", "default_user")
        
        # Save to episodic
        self.episodic_mem.store(user_id, f"User: {query}\nAssistant: {response}")
        
        # Save to semantic (only if it seems like a useful fact/experience)
        if len(query) > 20: # Simple heuristic
            self.semantic_mem.store(f"{user_id}_{len(query)}", f"In a previous conversation, the user asked: {query}. The answer was: {response}")
            
        return state

    def run(self, query: str, user_id: str = "default_user", thread_id: str = "1"):
        config = {"configurable": {"thread_id": thread_id}}
        input_state = {
            "messages": [HumanMessage(content=query)],
            "user_id": user_id
        }
        return self.graph.invoke(input_state, config)
