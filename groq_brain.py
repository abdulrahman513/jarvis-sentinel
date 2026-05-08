# groq_brain.py
import os
from groq import Groq
from dotenv import load_dotenv
from skills import JARVIS_TOOLS

load_dotenv()

class GroqBrain:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("CRITICAL: GROQ_API_KEY not found in .env file.")
            
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant" 
        print(f"[SYSTEM] Failover Brain Linked to: {self.model}")
        
        # Format tools for Groq to match Gemini's tool schema
        self.groq_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.__name__,
                    "description": tool.__doc__ or "Execute system command.",
                    "parameters": {"type": "object", "properties": {}, "required": []} 
                    # Basic parameter mapping; relies on exact text parsing for simple string passing
                }
            } for tool in JARVIS_TOOLS
        ]

    def think(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are J.A.R.V.I.S., an active SOC agent on Pop!_OS. "
                            "OUTPUT ONLY your final conversational response. NEVER output internal reasoning. "
                            "You are operating in EMERGENCY FAILOVER mode. "
                            "If an intrusion is detected, execute tools immediately."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            # Simulated tool execution router if Groq decides to call a tool
            message = completion.choices[0].message
            if message.tool_calls:
                tool_results = []
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    # Find matching Python function in skills
                    matching_func = next((f for f in JARVIS_TOOLS if f.__name__ == func_name), None)
                    if matching_func:
                        # Note: Deep parameter mapping requires a robust JSON parser, 
                        # for this failover we execute the tool directly if IP is in the prompt
                        import re
                        ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', prompt)
                        if ip_match and func_name == "block_malicious_ip":
                            res = matching_func(ip_match.group())
                            tool_results.append(f"{func_name} output: {res}")
                        elif func_name == "lock_screen":
                            res = matching_func()
                            tool_results.append(f"{func_name} output: {res}")
                return "\n".join(tool_results)
            
            return message.content
        except Exception as e:
            return f"[GROQ ERROR] Failover malfunction: {str(e)}"