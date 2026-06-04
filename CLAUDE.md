# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A lightweight personal blog built with FastAPI + Markdown files. No database — all content lives on the filesystem (Markdown posts with YAML frontmatter, JSON comment files). Written in Chinese (Simplified).

## Running the App

```bash
pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
```

The server runs at http://localhost:8000. There are no tests, no build step, and no linter configured.

## Architecture

**Two-module design:**

- `main.py` — FastAPI route layer. All HTTP endpoints live here (index, post detail, category, tag, search, about, info, comment submission). Routes call into `blog.py` for data and pass results to Jinja2 templates.
- `blog.py` — Core business logic. Handles Markdown parsing (`python-frontmatter` + `markdown` with Pygments code highlighting, TOC, fenced code, tables), pagination, search (case-insensitive substring match on title + rendered HTML), category/tag aggregation, and comment CRUD (JSON file per post).

**Data flow:** Markdown files in `posts/` → parsed by `blog._parse_post()` (frontmatter + rendered HTML) → consumed by routes → rendered via Jinja2 templates in `templates/`.

**Template inheritance:** All pages extend `templates/base.html`, which provides the nav (dynamically lists all categories), search form, and footer. The `_common_context()` helper in `main.py` injects `categories` and `tags` into every template response.

**Comments:** Stored as JSON files in `comments/` keyed by post slug (`comments/{slug}.json`). Submitted via AJAX (see `static/main.js`) to `POST /comment/{slug}` with form-encoded `name` and `content` fields.

## Adding Content

New posts go in `posts/` as `.md` files. The filename (minus `.md`) becomes the URL slug. Required frontmatter fields:

```yaml
---
title: "文章标题"
date: 2024-12-01
category: "分类名"
tags: ["标签1", "标签2"]
summary: "可选摘要，不填则自动截取正文前200字"
---
```

## Key Conventions

- Post slugs are derived from filenames — renaming a file changes the URL and breaks comment associations.
- `POSTS_PER_PAGE` (10) is defined in `blog.py`; pagination is offset-based.
- Comment IDs are sequential integers based on array position (not stable across deletions).
- CSS uses CSS variables with automatic dark mode via `prefers-color-scheme`.
- `BASE_DIR` is computed from `__file__` in both `main.py` and `blog.py` — paths assume the working directory is the project root.
