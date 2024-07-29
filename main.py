from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .database import create_db_and_tables
from .models.user_model import User
from .models.post_model import Post
from .routers import oauth

settings = config.get_settings()

app = FastAPI()

origins = [
    settings.allowed_origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oauth.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}