"""Resume Builder — FastAPI 入口"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.config import settings
from server.database import engine, Base
from server.routers import analyze, resumes, chat, export, skills


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时创建数据库表"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Resume Builder API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(skills.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "resume-builder"}


# 生产环境挂载前端静态文件（必须在最后）
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
