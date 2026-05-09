from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import database, brain, os, json, sqlite3, subprocess, uvicorn
from groq_brain import GroqBrain

app = FastAPI()
templates = Jinja2Templates(directory="templates")
jarvis = brain.JarvisBrain()
groq_fallback = GroqBrain()
CONFIG_PATH = "/home/rana/jarvis-sentinel/config.json"

# --- CORE HELPERS ---
def get_processed_incidents():
    raw_incidents = database.get_recent_incidents()
    processed = []
    for inc in raw_incidents:
        inc_list = list(inc)
        inc_list.append(database.is_blacklisted(inc[2])) # Index 9 = active status
        processed.append(inc_list)
    return processed

def get_ui_context(session_id=None):
    incidents = get_processed_incidents()
    sessions = database.get_all_sessions()
    
    if not session_id and sessions:
        session_id = sessions[0][0]
    elif not sessions:
        session_id = database.create_session()
        sessions = database.get_all_sessions()
        
    history = database.get_session_messages(session_id)
    
    with open(CONFIG_PATH, "r") as f:
        maint = json.load(f).get("policy_engine", {}).get("maintenance_mode", False)
        
    return {
        "incidents": incidents, 
        "sessions": sessions, 
        "current_session": session_id, 
        "chat_history": history, 
        "maint": maint
    }

# --- UI ROUTES ---
@app.get("/")
async def index(request: Request, session_id: int = None):
    ctx = get_ui_context(session_id)
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, **ctx})

@app.get("/get-queue")
async def get_queue(request: Request):
    return templates.TemplateResponse(request=request, name="partials/queue.html", context={"incidents": get_processed_incidents()})

# --- SESSION ROUTES ---
@app.post("/new-chat")
async def new_chat():
    session_id = database.create_session()
    return RedirectResponse(url=f"/?session_id={session_id}", status_code=303)

@app.post("/delete-chat/{session_id}")
async def delete_chat(session_id: int):
    database.delete_session(session_id)
    return RedirectResponse(url="/", status_code=303)

# --- ACTION ROUTES ---
@app.post("/chat")
async def chat_with_jarvis(message: str = Form(...), session_id: int = Form(...)):
    database.save_message(session_id, "USER", message)
    ctx_msg = f"Report stats: {database.get_report_stats()}. Query: {message}" if "report" in message.lower() else message
    try:
        response = jarvis.think(ctx_msg)
        if "500" in response: raise Exception()
    except:
        response = groq_fallback.think(ctx_msg)
        
    database.save_message(session_id, "JARVIS", response)
    return HTMLResponse(content=f"<div class='text-white/40 mb-1'>YOU: {message}</div><div class='text-green-400 mb-4'>JARVIS: {response}</div><script>document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;</script>")

@app.post("/pardon")
async def pardon_ip(ip: str = Form(...)):
    subprocess.run(["sudo", "ufw", "delete", "deny", "from", ip])
    conn = sqlite3.connect(database.DB_PATH)
    conn.execute("DELETE FROM blacklist WHERE ip_address = ?", (ip,))
    conn.commit()
    conn.close()
    return HTMLResponse(content="<span class='text-blue-500 font-bold uppercase text-[10px]'>Neutralized</span>")

@app.post("/toggle-maint")
async def toggle_maint():
    with open(CONFIG_PATH, "r+") as f:
        cfg = json.load(f); state = not cfg["policy_engine"]["maintenance_mode"]
        cfg["policy_engine"]["maintenance_mode"] = state
        f.seek(0); json.dump(cfg, f, indent=4); f.truncate()
    color = "text-orange-500 border-orange-500" if state else "text-gray-500 border-gray-800"
    return HTMLResponse(content=f"<button hx-post='/toggle-maint' hx-target='#maint-btn' hx-swap='outerHTML' class='border {color} px-2 py-1 uppercase text-[10px]'>MAINT: {'ON' if state else 'OFF'}</button>")

@app.post("/get-forensics")
async def get_forensics(path: str = Form(...)):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return HTMLResponse(content=f"<pre class='text-green-500 p-2'>{f.read()}</pre>")
    return HTMLResponse(content="<p class='text-gray-500 p-2'>Forensic payload not found.</p>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)