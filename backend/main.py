from fastapi import FastAPI, Request
from twilio.rest import Client
from dotenv import load_dotenv
import httpx
import os
from supabase import create_client
from datetime import datetime
import uuid

session_id = str(uuid.uuid4()),
# Load environment variables FIRST
load_dotenv()

# ========== ENV VARIABLES ==========
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_from = os.getenv("TWILIO_PHONE")      # e.g., whatsapp:+14155238886
twilio_to = os.getenv("MY_PHONE")            # e.g., whatsapp:+91xxxxxxxxxx
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ========== INIT CLIENTS ==========
twilio_client = Client(twilio_sid, twilio_token)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== FASTAPI APP ==========
app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI WhatsApp Bot is live!"}


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    user_msg = form.get("Body")

    # Call Groq API
    timeout_config = httpx.Timeout(10.0, connect=5.0)  # 10 seconds read, 5 seconds connect
    async with httpx.AsyncClient(timeout=timeout_config) as client:

        groq_response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI WhatsApp assistant."},
                    {"role": "user", "content": user_msg}
                ]
            }
        )

    groq_json = groq_response.json()
    print("Groq Full Response:", groq_response.status_code, groq_json)

    # Parse response
    if "choices" in groq_json:
        reply = groq_json["choices"][0]["message"]["content"]
    else:
        reply = "Sorry, I couldn't generate a reply. Please try again."

   
   

   
    supabase.table("messages").insert({
        
        "user_msg": user_msg,
        "ai_reply":"",
        "message_type": "user_msg",
        "session_id": session_id,
        "status": "sent",
        "is_error": False
     }).execute()
    
    supabase.table("messages").insert({
        
        "user_msg": "",
        "ai_reply":reply,
        "message_type": "user_msg",
        "session_id": session_id,
        "status": "sent",
        "is_error": False
     }).execute()
   
   
    # Send reply to WhatsApp
    twilio_client.messages.create(
        body=reply,
        from_=twilio_from,
        to=twilio_to
     )

    return {"status": "ok"}
