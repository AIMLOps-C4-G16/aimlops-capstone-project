from contextlib import asynccontextmanager
import os
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from models import ICModel, ImageDatabaseIndex

from config import settings
from captioning import captioning_router
from search import search_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("## Loading the Image Captioning model")
    settings.IC_MODEL.append(ICModel())

    if settings.IC_MODEL[0].status == "Model loaded":
        print("## Building the Image Database index")
        settings.IMAGE_DB_INDEX.append(ImageDatabaseIndex(settings.IC_MODEL[0], os.environ['HF_TOKEN']))

    yield

    print("## Cleaning up the Image Captioning model & Image Database index and releasing resources")
    settings.IMAGE_DB_INDEX.clear()
    settings.IC_MODEL.clear()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


root_router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIRECTORY)

@root_router.get("/")
def index(request: Request) -> Any:
    return templates.TemplateResponse("home.html", {"request": request, "name": settings.PROJECT_NAME})


app.include_router(root_router)
app.include_router(captioning_router)
app.include_router(search_router)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
