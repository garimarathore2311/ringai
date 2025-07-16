from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from utils.code_generator import generate_embed_code
from utils.file_parser import extract_text_from_pdf, extract_text_from_excel
from utils.web_scraper import scrape_website
import uuid
import os
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

user_db = {}  # temporary memory store

@router.get("/register", response_class=HTMLResponse)
async def get_registration_form(request: Request):
    return templates.TemplateResponse("embed_code.html", {"request": request, "embed_code": None})


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    website: str = Form(...),
    purpose: str = Form(...),
    question_type: str = Form(...),
    tone: str = Form(...),
    bot_name: str = Form("Chatbot"),
    file: list[UploadFile] = File(...)
):
    client_id = str(uuid.uuid4())
    full_text = ""
    saved_files = []

    # 1. Extract text from uploaded files
    for f in file:
        file_path = os.path.join(UPLOAD_DIR, f.filename)
        with open(file_path, "wb") as out_file:
            out_file.write(await f.read())
        saved_files.append(file_path)

        if f.filename.endswith(".pdf"):
            full_text += extract_text_from_pdf(file_path)
        elif f.filename.endswith((".xls", ".xlsx")):
            full_text += extract_text_from_excel(file_path)

    # 2. Scrape website content and append to text
    scraped_text = scrape_website(website)
    if scraped_text:
        full_text += "\n" + scraped_text

    # 3. Save combined raw text
    raw_path = f"{UPLOAD_DIR}/{client_id}_raw.txt"
    with open(raw_path, "w", encoding="utf-8") as text_file:
        text_file.write(full_text)

    # 4. Save user metadata
    user_data = {
        "client_id": client_id,
        "name": name,
        "email": email,
        "website": website,
        "purpose": purpose,
        "question_type": question_type,
        "tone": tone,
        "bot_name": bot_name,
        "uploaded_files": saved_files,
        "scraped_text_preview": scraped_text[:1000] if scraped_text else None
    }

    with open(f"{UPLOAD_DIR}/{client_id}_meta.json", "w", encoding="utf-8") as json_file:

        json.dump(user_data, json_file, indent=2)

    # 5. Build vector store — import inside the function to avoid circular import
    from rag_engine import build_vector_store
    build_vector_store(bot_name)

    # Store user data in memory (optional)
    user_db[client_id] = user_data

    embed_code = generate_embed_code(client_id)
    return templates.TemplateResponse("embed_code.html", {
        "request": request,
        "embed_code": embed_code,
        "client_id": client_id  # ✅ Add this for "Test Your Bot" button
    })
