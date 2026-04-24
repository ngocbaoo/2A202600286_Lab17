import jsonlines
import os
from typing import List, Dict, Any
from src.memory.base import BaseMemory

class EpisodicJSONMemory(BaseMemory):
    def __init__(self, file_path: str):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def store(self, key: str, value: Any, metadata: Dict = None):
        """Append an episode to the log."""
        episode = {
            "session_id": key,
            "content": value,
            "metadata": metadata or {}
        }
        with jsonlines.open(self.file_path, mode='a') as writer:
            writer.write(episode)

    def retrieve(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for episodes. Simple keyword search for now."""
        episodes = []
        if not os.path.exists(self.file_path):
            return []
            
        with jsonlines.open(self.file_path) as reader:
            for obj in reader:
                if query.lower() in str(obj["content"]).lower():
                    episodes.append(obj)
        
        return episodes[-limit:]

    def clear(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
