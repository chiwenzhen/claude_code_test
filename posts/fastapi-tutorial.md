---
title: "FastAPI 快速入门指南"
date: 2024-12-15
category: "技术"
tags: ["Python", "FastAPI", "教程"]
summary: "一篇简明的 FastAPI 入门教程，从零开始搭建一个 REST API。"
---

## 什么是 FastAPI

FastAPI 是一个用于构建 API 的现代、高性能 Python Web 框架。它的特点：

- **快速**：与 NodeJS 和 Go 相当的性能
- **易学**： intuitive 的 API 设计
- **自动文档**：内置 Swagger UI

## 安装

```bash
pip install fastapi uvicorn
```

## 最简示例

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/users/{user_id}")
def read_user(user_id: int, q: str = None):
    return {"user_id": user_id, "query": q}
```

启动服务：

```bash
uvicorn main:app --reload
```

## 数据验证

FastAPI 使用 Pydantic 进行数据验证：

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int = 0  # 可选字段，默认值为 0

@app.post("/users")
def create_user(user: User):
    return user
```

## 依赖注入

```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items")
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

## 总结

FastAPI 是一个优秀的框架，适合：

| 场景 | 推荐度 |
|------|--------|
| REST API | ⭐⭐⭐⭐⭐ |
| 微服务 | ⭐⭐⭐⭐⭐ |
| 全栈 Web | ⭐⭐⭐ |
| 实时应用 | ⭐⭐⭐⭐ |

如果你还没有尝试过 FastAPI，强烈推荐去试试！
