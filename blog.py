"""
博客核心逻辑：加载 Markdown 文章、搜索、分类/标签、评论管理
"""

import os
import json
import frontmatter
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from datetime import datetime
from typing import Optional


# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BASE_DIR, "posts")
COMMENTS_DIR = os.path.join(BASE_DIR, "comments")

# Markdown 扩展
MD_EXTENSIONS = [
    CodeHiliteExtension(css_class="codehilite", guess_lang=True),
    FencedCodeExtension(),
    TableExtension(),
    TocExtension(permalink=True),
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
]

# 分页配置
POSTS_PER_PAGE = 10


def _render_markdown(content: str) -> str:
    """将 Markdown 内容渲染为 HTML"""
    return markdown.markdown(content, extensions=MD_EXTENSIONS)


def _parse_post(filepath: str) -> Optional[dict]:
    """解析单个 Markdown 文件，返回文章数据"""
    try:
        post = frontmatter.load(filepath)
        slug = os.path.splitext(os.path.basename(filepath))[0]

        # 必须包含 title 和 date
        if "title" not in post or "date" not in post:
            return None

        # 渲染正文
        html_content = _render_markdown(post.content)

        # 摘要：优先使用 frontmatter 中的 summary，否则截取正文前 200 字
        summary = post.get("summary", "")
        if not summary:
            plain_text = post.content[:200]
            # 截取到最后一个完整句子
            for sep in ["。", ".", "\n\n", "\n"]:
                idx = plain_text.rfind(sep)
                if idx > 50:
                    plain_text = plain_text[:idx + len(sep)]
                    break
            summary = plain_text + "..."

        # 处理日期
        date = post["date"]
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        elif isinstance(date, datetime):
            date = date.date()

        return {
            "slug": slug,
            "title": post["title"],
            "date": date,
            "date_str": date.strftime("%Y-%m-%d"),
            "category": post.get("category", "未分类"),
            "tags": post.get("tags", []),
            "summary": summary,
            "content": html_content,
        }
    except Exception as e:
        print(f"解析文章失败 {filepath}: {e}")
        return None


def load_all_posts() -> list[dict]:
    """加载所有文章，按日期倒序"""
    posts = []
    if not os.path.isdir(POSTS_DIR):
        return posts

    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(POSTS_DIR, filename)
        post = _parse_post(filepath)
        if post:
            posts.append(post)

    # 按日期倒序
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def load_post(slug: str) -> Optional[dict]:
    """根据 slug 加载单篇文章"""
    filepath = os.path.join(POSTS_DIR, f"{slug}.md")
    if not os.path.isfile(filepath):
        return None
    return _parse_post(filepath)


def get_paginated_posts(page: int = 1, per_page: int = POSTS_PER_PAGE) -> dict:
    """分页获取文章"""
    all_posts = load_all_posts()
    total = len(all_posts)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page

    return {
        "posts": all_posts[start:end],
        "page": page,
        "total_pages": total_pages,
        "total_posts": total,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }


def get_posts_by_category(category: str) -> list[dict]:
    """按分类获取文章"""
    return [p for p in load_all_posts() if p["category"] == category]


def get_posts_by_tag(tag: str) -> list[dict]:
    """按标签获取文章"""
    return [p for p in load_all_posts() if tag in p["tags"]]


def search_posts(query: str) -> list[dict]:
    """搜索文章（标题 + 正文，不区分大小写）"""
    if not query.strip():
        return []

    q = query.lower()
    results = []
    for post in load_all_posts():
        if q in post["title"].lower() or q in post["content"].lower():
            results.append(post)
    return results


def get_all_categories() -> list[dict]:
    """获取所有分类及文章数量"""
    counts: dict[str, int] = {}
    for post in load_all_posts():
        cat = post["category"]
        counts[cat] = counts.get(cat, 0) + 1
    return [{"name": k, "count": v} for k, v in sorted(counts.items())]


def get_all_tags() -> list[dict]:
    """获取所有标签及文章数量"""
    counts: dict[str, int] = {}
    for post in load_all_posts():
        for tag in post["tags"]:
            counts[tag] = counts.get(tag, 0) + 1
    return [{"name": k, "count": v} for k, v in sorted(counts.items())]


# --- 评论功能 ---

def _comment_filepath(slug: str) -> str:
    """评论文件路径"""
    os.makedirs(COMMENTS_DIR, exist_ok=True)
    return os.path.join(COMMENTS_DIR, f"{slug}.json")


def load_comments(slug: str) -> list[dict]:
    """加载某篇文章的所有评论"""
    filepath = _comment_filepath(slug)
    if not os.path.isfile(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_comment(slug: str, name: str, content: str) -> dict:
    """保存一条新评论"""
    comments = load_comments(slug)
    comment = {
        "id": len(comments) + 1,
        "name": name,
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    comments.append(comment)

    filepath = _comment_filepath(slug)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    return comment
