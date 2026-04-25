import sqlite3

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE = os.getenv("DATABASE")

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")