from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import BASE_DIR, STATIC_DIR, TEMPLATES_DIR
from app.database import init_db
from app.routers.api import router as api_router

app = FastAPI(title="Bandcamp-Hub")

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
