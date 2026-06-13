from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import news, history, favorite, users
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


@app.get("/")
async def root():
    return {"message": "Hello FastAPI"}


app.include_router(news.router)
app.include_router(history.router)
app.include_router(users.router)
app.include_router(favorite.router)
