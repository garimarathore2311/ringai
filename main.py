# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routers import user, chat, chat_ui  # <-- ✅ this line
import spacy.cli
spacy.cli.download("en_core_web_sm")


app = FastAPI()
import os
os.makedirs("uploads", exist_ok=True)
os.path.exists("uploads/abfa8742-ec9a-43fb-bd46-0c62d0aae0f0_meta.json")
# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates & Static
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Include Routes
app.include_router(user.router)
app.include_router(chat_ui.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"msg": "Welcome to GarimaBot!"}


