from abc import ABC, abstractmethod
from typing import Any, List, Dict

class BaseMemory(ABC):
    @abstractmethod
    def store(self, key: str, value: Any, metadata: Dict = None):
        """Store information in memory."""
        pass

    @abstractmethod
    def retrieve(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant information from memory."""
        pass

    @abstractmethod
    def clear(self):
        """Clear the memory backend."""
        pass
