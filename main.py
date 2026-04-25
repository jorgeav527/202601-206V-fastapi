import sqlite3

from fastapi import FastAPI, Request, HTTPException, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

DATABASE = os.getenv("DATABASE")

app = FastAPI()

templates = Jinja2Templates(directory="templates")





@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created: str


def get_post_or_404(post_id: int):
    with get_db_connection() as conn:
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        return dict(post)
    
@app.get("/post/{id}")
def get_post_detail(id: int):
    return get_post_or_404(id)
    

@app.post("/post-create", status_code=201)
def create_one_post(post: PostCreate):
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            (post.title, post.content),
        )
        conn.commit()
        last_id = cursor.lastrowid
    return {"id": last_id, "title": post.title, "content": post.content}


@app.get("/post-all", response_model=list[PostResponse])
def get_all_post():
    with get_db_connection() as conn:
        posts = conn.execute("SELECT * FROM posts").fetchall()
    return [dict(row) for row in posts]


@app.get("/post-table", response_class=HTMLResponse)
def get_post_table(request: Request):  # Add request for Jinja
    with get_db_connection() as conn:
        posts = conn.execute("SELECT * FROM posts").fetchall()
    return templates.TemplateResponse(
        request, "partials/table.html", context={"posts": posts}
    )


@app.post("/post-ui")
def create_from_ui(title: str = Form(...), content: str = Form(...)):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
        )
        conn.commit()
    return HTMLResponse(
        content=f"<b>Success!</b> Created post: {title}: {content}. Click 'Load All Posts' to see it."
    )

@app.get("/posts/search", response_class=HTMLResponse)
def search_posts(request: Request, q: str = Query(...)):
    search_term = f"%{q}%" # q=primer

    with get_db_connection() as conn:
        posts = conn.execute(
            "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ?",
            (search_term, search_term),
        ).fetchall()

    # Reuse your existing Jinja partial to render the results!
    return templates.TemplateResponse(
        request, "partials/table.html", context={"posts": posts}
    )