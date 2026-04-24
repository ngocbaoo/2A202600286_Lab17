import redis
import json
import logging
from typing import List, Dict, Any
from src.memory.base import BaseMemory

class LongTermRedisMemory(BaseMemory):
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.client.ping()
            self.use_mock = False
        except Exception as e:
            logging.warning(f"Redis connection failed: {e}. Using mock memory.")
            self.use_mock = True
            self.mock_db = {}

    def store(self, key: str, value: Any, metadata: Dict = None):
        data = {"value": value, "metadata": metadata}
        if self.use_mock:
            self.mock_db[key] = json.dumps(data)
        else:
            self.client.set(key, json.dumps(data))

    def retrieve(self, query: str, limit: int = 5) -> List[Dict]:
        """
        In a real scenario, we might use Redis Search or key-based lookup.
        For this lab, we'll assume the router provides a key or we scan relevant keys.
        """
        results = []
        if self.use_mock:
            # Simple mock: return everything if it matches key-ish
            for k, v in self.mock_db.items():
                if query.lower() in k.lower():
                    results.append(json.loads(v))
        else:
            keys = self.client.keys(f"*{query}*")
            for k in keys[:limit]:
                val = self.client.get(k)
                if val:
                    results.append(json.loads(val))
        return results

    def clear(self):
        if self.use_mock:
            self.mock_db = {}
        else:
            self.client.flushdb()
