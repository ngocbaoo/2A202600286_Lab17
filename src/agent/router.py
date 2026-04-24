from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class MemoryRouting(BaseModel):
    """Classify the intent of the user query for memory retrieval."""
    use_long_term: bool = Field(description="True if the query relates to user preferences, personal details, or persistent settings.")
    use_semantic: bool = Field(description="True if the query requires factual knowledge or specific information from past documents.")
    use_episodic: bool = Field(description="True if the query refers to specific past conversation episodes or experiences.")
    reasoning: str = Field(description="Brief explanation for the routing decision.")

class MemoryRouter:
    def __init__(self, model: ChatOpenAI):
        self.model = model.with_structured_output(MemoryRouting)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a memory routing assistant. Analyze the user query and decide which memory systems should be queried."),
            ("user", "{query}")
        ])

    def route(self, query: str) -> MemoryRouting:
        chain = self.prompt | self.model
        return chain.invoke({"query": query})
