import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any
from src.memory.base import BaseMemory

class SemanticChromaMemory(BaseMemory):
    def __init__(self, path: str, collection_name: str = "agent_memory", api_key: str = None):
        self.client = chromadb.PersistentClient(path=path)
        # Using a simple default embedding function or OpenAI if key provided
        if api_key:
            self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=api_key,
                api_base="https://models.inference.ai.azure.com",
                model_name="text-embedding-3-small"
            )
        else:
            # Fallback to default (SentenceTransformer if installed, or error)
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            
        self.collection = self.client.get_or_create_collection(
            name=collection_name, 
            embedding_function=self.embedding_fn
        )

    def store(self, key: str, value: str, metadata: Dict = None):
        final_metadata = metadata or {}
        if not final_metadata:
            final_metadata = {"source": "agent_memory"}
        
        self.collection.add(
            documents=[value],
            metadatas=[final_metadata],
            ids=[key]
        )

    def retrieve(self, query: str, limit: int = 5) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        # Format results
        formatted = []
        if results['documents']:
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                formatted.append({"content": doc, "metadata": meta})
        return formatted

    def clear(self):
        # Delete and recreate collection
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name, 
            embedding_function=self.embedding_fn
        )
