import json
import os
import sys
import time
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.graph import MultiMemoryAgent

load_dotenv()

class BenchmarkRunner:
    def __init__(self):
        self.model_config = {
            "api_key": os.getenv("GITHUB_TOKEN"),
            "base_url": os.getenv("AZURE_INFERENCE_ENDPOINT"),
            "model_name": os.getenv("AZURE_INFERENCE_MODEL")
        }
        self.memory_config = {
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", 6379)),
            "episodic_path": os.getenv("EPISODIC_LOG_PATH", "./data/episodes.jsonl"),
            "chroma_path": os.getenv("CHROMA_PATH", "./data/chroma")
        }
        
        self.agent = MultiMemoryAgent(self.model_config, self.memory_config)
        self.judge_llm = ChatOpenAI(
            api_key=self.model_config["api_key"],
            base_url=self.model_config["base_url"],
            model=self.model_config["model_name"],
            max_retries=10
        )

    def run_case(self, case: dict, use_memory: bool = True):
        results = []
        # Clear memory for a fresh start if needed, but for multi-turn, we want it to persist across turns
        if use_memory:
            self.agent.redis_mem.clear()
            self.agent.semantic_mem.clear()
            self.agent.episodic_mem.clear()
        
        thread_id = f"test_{case['id']}_{'mem' if use_memory else 'nomem'}"
        
        for turn in case["turns"]:
            start_time = time.time()
            
            # If not using memory, we'd ideally bypass the recall node.
            # For simplicity, we can just clear memory before each turn if use_memory=False
            if not use_memory:
                self.agent.redis_mem.clear()
                self.agent.semantic_mem.clear()
                self.agent.episodic_mem.clear()

            response = self.agent.run(turn["query"], user_id="tester", thread_id=thread_id)
            latency = time.time() - start_time
            
            last_msg = response["messages"][-1].content
            memories_used = response.get("memories", [])
            
            # Token count (rough estimate)
            tokens = len(last_msg.split()) # Placeholder for real token count
            
            results.append({
                "turn": turn["query"],
                "response": last_msg,
                "memories": memories_used,
                "latency": latency,
                "tokens": tokens
            })
            
        return results

    def judge_results(self, case: dict, mem_results: list, nomem_results: list):
        # Use LLM to judge relevance and accuracy
        eval_prompt = f"""
        Compare two AI agent sessions for the following case: {case['name']}
        Case Difficulty: {case['difficulty']}
        
        Session A (With Memory):
        {json.dumps(mem_results, indent=2)}
        
        Session B (Without Memory):
        {json.dumps(nomem_results, indent=2)}
        
        Rate both sessions from 0-10 on:
        1. Relevance: Did it remember what it was supposed to?
        2. Context Utilization: How well did it use the memories?
        3. Token Efficiency: Was the response concise and accurate?
        
        Return a JSON object with scores and brief reasoning.
        """
        
        res = self.judge_llm.invoke([HumanMessage(content=eval_prompt)])
        # In a real script, we'd parse this JSON. For now, we'll just store the text.
        return res.content

    def run_all(self, cases_path: str):
        with open(cases_path, 'r') as f:
            cases = json.load(f)
            
        report_data = []
        
        for case in cases:
            print(f"Running case: {case['name']}...")
            mem_res = self.run_case(case, use_memory=True)
            nomem_res = self.run_case(case, use_memory=False)
            
            evaluation = self.judge_results(case, mem_res, nomem_res)
            
            # Small sleep to respect rate limits
            time.sleep(2)
            
            report_data.append({
                "case": case["name"],
                "difficulty": case["difficulty"],
                "mem_latency": sum(r['latency'] for r in mem_res) / len(mem_res),
                "nomem_latency": sum(r['latency'] for r in nomem_res) / len(nomem_res),
                "mem_hit_rate": len([r for r in mem_res if r['memories']]) / len(mem_res),
                "evaluation": evaluation
            })
            
        df = pd.DataFrame(report_data)
        df.to_csv("benchmark_results.csv", index=False)
        return df

if __name__ == "__main__":
    print("Starting Benchmark Runner...")
    runner = BenchmarkRunner()
    print("Initialization complete. Running all cases...")
    runner.run_all("benchmark/cases.json")
    print("Benchmark complete!")
