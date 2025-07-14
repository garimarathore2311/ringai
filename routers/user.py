# routers/user.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uuid
from utils.code_generator import generate_embed_code

router = APIRouter()
templates = Jinja2Templates(directory="templates")

user_db = {}  # use real DB later

@router.get("/register", response_class=HTMLResponse)
async def get_registration_form(request: Request):
    return templates.TemplateResponse("embed_code.html", {"request": request, "embed_code": None})

@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    website: str = Form(...),
    purpose: str = Form(...)
):
    client_id = str(uuid.uuid4())
    user_db[client_id] = {
        "name": name,
        "email": email,
        "website": website,
        "purpose": purpose
    }
    embed_code = generate_embed_code(client_id)
    return templates.TemplateResponse("embed_code.html", {"request": request, "embed_code": embed_code})
