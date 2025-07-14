# routers/chat_ui.py
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/chatbot/{client_id}")
async def render_chatbot(request: Request, client_id: str):
    meta_path = f"uploads/{client_id}_meta.json"
    if not os.path.exists(meta_path):
        return templates.TemplateResponse("error.html", {"request": request, "message": "Bot not found."})

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    return templates.TemplateResponse("chatbot_ui.html", {
        "request": request,
        "client_id": client_id,
        "bot_name": meta.get("bot_name", "Chatbot")
    })