# brain.py
import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from dotenv import load_dotenv
from skills import JARVIS_TOOLS

class JarvisBrain:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("CRITICAL: GEMINI_API_KEY not found in .env file.")
            
        genai.configure(api_key=api_key)
        
        # --- SELF-HEALING DISCOVERY PHASE ---
        print("[SYSTEM] Interrogating API for available models...")
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Filter out 2.5 and 2.0 to avoid the strict 20-request daily limits
        safe_models = [m for m in available_models if "2.5" not in m and "2.0" not in m]
        
        # Force fallback to the high-quota 1.5 models
        priority_models = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-1.0-pro"
        ]
        
        self.model_id = next((m for m in priority_models if m in safe_models), None)
        
        if not self.model_id:
            # Absolute fallback
            self.model_id = safe_models[0] if safe_models else available_models[0]
            
        print(f"[SYSTEM] Brain Linked to: {self.model_id}")
        # ------------------------------------

        self.model = genai.GenerativeModel(
            model_name=self.model_id,
            tools=JARVIS_TOOLS,
            system_instruction=(
                "CRITICAL INSTRUCTION: You are J.A.R.V.I.S., an active system agent. "
                "YOU MUST NEVER output your internal reasoning, 'Plan:', or thought process to the user. "
                "OUTPUT ONLY your final conversational response. "
                "If asked to notify, you MUST execute the 'trigger_visual_alert' function."
            )
        )
        
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def think(self, user_input: str) -> str:
        try:
            response = self.chat.send_message(user_input)
            return response.text
        except Exception as e:
            return f"[ERROR] Brain malfunction: {str(e)}"