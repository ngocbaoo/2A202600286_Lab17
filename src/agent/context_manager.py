import tiktoken
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

class ContextManager:
    def __init__(self, max_tokens: int = 4000, model_name: str = "gpt-4o-mini"):
        self.max_tokens = max_tokens
        try:
            self.encoder = tiktoken.encoding_for_model(model_name)
        except:
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def manage(self, 
               system_message: str, 
               user_query: str, 
               recalled_memories: List[str], 
               history: List[BaseMessage]) -> List[BaseMessage]:
        
        # 1. System Prompt (Highest Priority)
        sys_tokens = self.count_tokens(system_message)
        
        # 2. User Query
        user_tokens = self.count_tokens(user_query)
        
        current_total = sys_tokens + user_tokens
        
        # 3. Handle Memories (Level 3)
        available_memories = []
        memory_tokens = 0
        for mem in recalled_memories:
            m_tokens = self.count_tokens(mem)
            if current_total + memory_tokens + m_tokens < self.max_tokens * 0.8: # Reserve space for history
                available_memories.append(mem)
                memory_tokens += m_tokens
            else:
                break
        
        current_total += memory_tokens
        
        # 4. Handle History (Level 4 - Lowest Priority)
        final_history = []
        # Add history in reverse (most recent first) until limit reached
        for msg in reversed(history):
            msg_tokens = self.count_tokens(msg.content)
            if current_total + msg_tokens < self.max_tokens:
                final_history.insert(0, msg)
                current_total += msg_tokens
            else:
                break
                
        # Construct final message list
        messages = [SystemMessage(content=system_message)]
        
        # Sectioned Memory Injection
        if recalled_memories:
            profile_mem = [m for m in recalled_memories if "[User Preference]" in m]
            semantic_mem = [m for m in recalled_memories if "[Factual Recall]" in m]
            episodic_mem = [m for m in recalled_memories if "[Experience Recall]" in m]
            
            mem_content = "--- RECALLED CONTEXT ---\n"
            if profile_mem:
                mem_content += "\n[USER PROFILE]\n" + "\n".join(profile_mem)
            if semantic_mem:
                mem_content += "\n[FACTUAL KNOWLEDGE]\n" + "\n".join(semantic_mem)
            if episodic_mem:
                mem_content += "\n[PAST EPISODES]\n" + "\n".join(episodic_mem)
            mem_content += "\n------------------------"
            
            messages.append(SystemMessage(content=mem_content))
        
        messages.extend(final_history)
        messages.append(HumanMessage(content=user_query))
        
        return messages
