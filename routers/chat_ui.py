from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/chatbot/{client_id}", response_class=HTMLResponse)
async def chatbot_ui(request: Request, client_id: str):
    meta_path = f"uploads/{client_id}_meta.json"
    print(f"🧪 [DEBUG] Looking for metadata: {meta_path}")
    
    if not os.path.exists(meta_path):
        print(f"❌ [ERROR] File not found: {meta_path}")
        return templates.TemplateResponse("error.html", {"request": request, "error_message": "Bot not found."})

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return templates.TemplateResponse("chatbot_ui.html", {
        "request": request,
        "metadata": metadata,
        "client_id": client_id,
        "bot_name": metadata.get("bot_name", "Chatbot")
    })
