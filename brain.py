# brain.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from skills import JARVIS_TOOLS

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Hardcoded to your preferred model
TARGET_MODEL = "models/gemma-4-26b-a4b-it"

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_forensic_summary(summary_path: str) -> str:
    """Uses Gemma-4 to analyze forensic intent."""
    if not os.path.exists(summary_path) or summary_path == "N/A":
        return "Minimal reconnaissance detected; no payload captured."
    try:
        with open(summary_path, "r") as f:
            forensic_data = f.read()
            
        response = client.models.generate_content(
            model=TARGET_MODEL,
            config=types.GenerateContentConfig(
                system_instruction="Senior SOC Analyst mode. Identify intent from packet flags and hex data. Output 2 sentences max."
            ),
            contents=f"Analyze this threat forensic data:\n{forensic_data}"
        )
        return response.text.strip()
    except Exception as e:
        return f"Gemma-4 Analysis Failed: {e}"

class JarvisBrain:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("CRITICAL: GEMINI_API_KEY missing.")
        
        print(f"[SYSTEM] Brain Linked to: {TARGET_MODEL}")
        
        self.config = types.GenerateContentConfig(
            system_instruction=(
                "You are J.A.R.V.I.S., an active SOC agent on Pop!_OS. "
                "OUTPUT ONLY your final conversational response. "
                "If an intrusion is detected, coordinate with the Sentinel system to neutralize it."
            ),
            tools=JARVIS_TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
        )
        self.chat = client.chats.create(model=TARGET_MODEL, config=self.config)

    def think(self, user_input: str) -> str:
        try:
            response = self.chat.send_message(user_input)
            return response.text
        except Exception as e:
            return f"[ERROR] Brain malfunction: {str(e)}"