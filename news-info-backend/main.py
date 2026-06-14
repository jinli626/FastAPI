import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import news, history, favorite, users, admin_auth, admin_news, admin_category, admin_stats, upload
from utils.exception_handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态资源目录（封面图等上传文件）
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}


app.include_router(news.router)
app.include_router(history.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(admin_auth.router)
app.include_router(admin_news.router)
app.include_router(admin_category.router)
app.include_router(admin_stats.router)
app.include_router(upload.router)
