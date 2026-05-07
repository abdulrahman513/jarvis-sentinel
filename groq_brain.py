import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqBrain:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Using the High-Volume 8B model for security sweeps
        self.model = "llama-3.1-8b-instant" 

    def think(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are J.A.R.V.I.S., a security AI. Analyze logs and provide defensive actions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, # Low temp for precise security logic
                max_tokens=500
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"[GROQ ERROR] {e}"