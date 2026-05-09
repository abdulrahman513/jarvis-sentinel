# app.py
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import database, brain, os, json, sqlite3, subprocess, uvicorn
from groq_brain import GroqBrain

app = FastAPI()
templates = Jinja2Templates(directory="templates")
jarvis = brain.JarvisBrain()
groq_fallback = GroqBrain()
CONFIG_PATH = "/home/rana/jarvis-sentinel/config.json"

@app.get("/")
async def index(request: Request):
    incidents = database.get_recent_incidents()
    history = database.get_chat_history()
    with open(CONFIG_PATH, "r") as f:
        maint = json.load(f).get("policy_engine", {}).get("maintenance_mode", False)
    
    return templates.TemplateResponse(
        request=request, name="index.html", 
        context={"request": request, "incidents": incidents, "chat_history": history, "maint": maint}
    )

@app.post("/chat")
async def chat_with_jarvis(message: str = Form(...)):
    database.save_chat("USER", message)
    
    # Deterministic Reporting Logic
    if "report" in message.lower():
        stats = database.get_report_stats()
        context_msg = f"Generate a SOC report based on these DB stats: {stats}. Original user request: {message}"
    else:
        context_msg = message

    try:
        response = jarvis.think(context_msg)
        if "500" in response or not response: raise Exception()
    except:
        response = groq_fallback.think(context_msg)
    
    database.save_chat("JARVIS", response)
    return HTMLResponse(content=f"<div class='text-white/40 mb-1'>YOU: {message}</div><div class='text-green-400 mb-4'>JARVIS: {response}</div>")

@app.post("/pardon")
async def pardon_ip(ip: str = Form(...)):
    # ENTERPRISE PARDON
    subprocess.run(["sudo", "ufw", "delete", "deny", "from", ip])
    conn = sqlite3.connect(database.DB_PATH)
    conn.execute("DELETE FROM blacklist WHERE ip_address = ?", (ip,))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<span class='text-blue-500 font-bold uppercase text-[10px]'>Neutralized</span>")

@app.post("/toggle-maint")
async def toggle_maint():
    with open(CONFIG_PATH, "r+") as f:
        cfg = json.load(f)
        new_state = not cfg["policy_engine"]["maintenance_mode"]
        cfg["policy_engine"]["maintenance_mode"] = new_state
        f.seek(0); json.dump(cfg, f, indent=4); f.truncate()
    
    color = "text-orange-500 border-orange-500" if new_state else "text-gray-600 border-gray-800"
    return HTMLResponse(content=f"<button hx-post='/toggle-maint' hx-target='#maint-btn' hx-swap='outerHTML' class='border {color} px-2 py-1 uppercase text-[10px]'>MAINT: {'ON' if new_state else 'OFF'}</button>")

@app.post("/get-forensics")
async def get_forensics(path: str = Form(...)):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return HTMLResponse(content=f"<pre class='text-green-500 p-2'>{f.read()}</pre>")
    return HTMLResponse(content="<p class='text-gray-600 p-2'>Forensic payload not found.</p>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)