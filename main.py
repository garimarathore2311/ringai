# main.py
import os  # <-- Move this to the top

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routers import user, chat, chat_ui
import spacy.cli
spacy.cli.download("en_core_web_sm")

from dotenv import load_dotenv
from openai import OpenAI
from openai import AzureOpenAI

# ---------- Env & Client ----------
load_dotenv()

AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_KEY")
AOAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not (AOAI_ENDPOINT and AOAI_KEY and AOAI_DEPLOYMENT):
    raise RuntimeError("Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT in .env")

client = AzureOpenAI(
    api_key=AOAI_KEY,
    azure_endpoint=AOAI_ENDPOINT,
    api_version=AOAI_API_VERSION
)

app = FastAPI()
os.makedirs("uploads", exist_ok=True)
# os.path.exists("uploads/abfa8742-ec9a-43fb-bd46-0c62d0aae0f0_meta.json")  # <-- Remove or comment out

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

@app.get("/assistants")
def get_assistants():
    return {"msg": "Assistants endpoint is working"}


