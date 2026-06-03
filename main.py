"""
个人博客 — FastAPI 路由
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import blog
import os

app = FastAPI(title="我的个人博客")

# 静态文件和模板
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def _common_context(request: Request) -> dict:
    """公共模板上下文"""
    return {
        "request": request,
        "categories": blog.get_all_categories(),
        "tags": blog.get_all_tags(),
    }


# ── 首页 ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page: int = 1):
    data = blog.get_paginated_posts(page)
    ctx = _common_context(request)
    ctx.update(data)
    return templates.TemplateResponse("index.html", ctx)


# ── 文章详情 ──────────────────────────────────────────

@app.get("/post/{slug}", response_class=HTMLResponse)
async def post_detail(request: Request, slug: str):
    post = blog.load_post(slug)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    comments = blog.load_comments(slug)
    ctx = _common_context(request)
    ctx["post"] = post
    ctx["comments"] = comments
    return templates.TemplateResponse("post.html", ctx)


# ── 分类 ──────────────────────────────────────────────

@app.get("/category/{name}", response_class=HTMLResponse)
async def category(request: Request, name: str):
    posts = blog.get_posts_by_category(name)
    ctx = _common_context(request)
    ctx["posts"] = posts
    ctx["category_name"] = name
    return templates.TemplateResponse("category.html", ctx)


# ── 标签 ──────────────────────────────────────────────

@app.get("/tag/{name}", response_class=HTMLResponse)
async def tag(request: Request, name: str):
    posts = blog.get_posts_by_tag(name)
    ctx = _common_context(request)
    ctx["posts"] = posts
    ctx["tag_name"] = name
    return templates.TemplateResponse("tag.html", ctx)


# ── 搜索 ──────────────────────────────────────────────

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    posts = blog.search_posts(q)
    ctx = _common_context(request)
    ctx["posts"] = posts
    ctx["query"] = q
    return templates.TemplateResponse("search.html", ctx)


# ── 关于 ──────────────────────────────────────────────

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    ctx = _common_context(request)
    return templates.TemplateResponse("about.html", ctx)


# ── 评论 ──────────────────────────────────────────────

@app.post("/comment/{slug}")
async def add_comment(slug: str, name: str = Form(...), content: str = Form(...)):
    # 验证文章存在
    post = blog.load_post(slug)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 验证输入
    name = name.strip()
    content = content.strip()
    if not name or not content:
        return JSONResponse(
            status_code=400,
            content={"error": "昵称和内容不能为空"},
        )
    if len(content) > 1000:
        return JSONResponse(
            status_code=400,
            content={"error": "评论内容不能超过 1000 字"},
        )

    comment = blog.save_comment(slug, name, content)
    return JSONResponse(content=comment)
