from contextlib import asynccontextmanager
import os
import shutil
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from models import ICModel, ImageDatabaseIndex

from config import settings
from captioning import captioning_router
from indexing import indexing_router
from search import search_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("## Loading the Image Captioning model")
    settings.SHARED["IC_MODEL"] = ICModel()
    
    print("## Building the Image Database index")
    if os.path.exists(settings.USER_IMAGE_DB_DIRECTORY):
        shutil.rmtree(settings.USER_IMAGE_DB_DIRECTORY)
    os.makedirs(settings.USER_IMAGE_DB_DIRECTORY)

    settings.SHARED["IMAGE_DB_INDEX"] = ImageDatabaseIndex(os.environ['HF_TOKEN'])

    yield

    print("## Cleaning up the Image Captioning model & Image Database index and releasing resources")
    settings.SHARED.clear()
    shutil.rmtree(settings.USER_IMAGE_DB_DIRECTORY)

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
app.include_router(indexing_router)
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
