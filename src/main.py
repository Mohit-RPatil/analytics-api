from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.events.routing import router as event_router
from src.api.events.sessions import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], # allow all origin
    allow_credentials = True,
    allow_methods = ["*"], # allow all methods
    allow_headers = ["*"], # allow all headers
)
app.include_router(event_router, prefix="/src/api/events")

@app.get("/")
def read_root():
    return {"Hello World"}


@app.get("/healthz")
def read_api_health():
    return {"Status" : "Ok"}