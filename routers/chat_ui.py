from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/chatbot/{client_id}", response_class=HTMLResponse)
async def chatbot_ui(request: Request, client_id: str):
    # Search for metadata file inside uploads/ subfolders
    bot_dir = None
    for folder in os.listdir("uploads"):
        folder_path = os.path.join("uploads", folder)
        if os.path.isdir(folder_path):
            meta_path = os.path.join(folder_path, "meta.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    if metadata.get("client_id") == client_id:
                        bot_dir = folder
                        break

    if not bot_dir:
        print(f"❌ [ERROR] Metadata for client_id {client_id} not found.")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Bot not found. Please register first."
        })

    # Load metadata again now that we know the correct path
    meta_path = os.path.join("uploads", bot_dir, "meta.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return templates.TemplateResponse("chatbot_ui.html", {
        "request": request,
        "metadata": metadata,
        "client_id": client_id,
        "bot_name": metadata.get("bot_name", "Chatbot")
    })
