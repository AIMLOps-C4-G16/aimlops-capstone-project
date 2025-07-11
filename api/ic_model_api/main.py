from contextlib import asynccontextmanager
import base64
import tempfile
from typing import Any

from fastapi import APIRouter, FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

#from api import api_router
from ic_model import ICModel
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("## Loading the Image Captioning model")
    settings.IC_MODEL.append(ICModel())

    yield

    print("## Cleaning up the Image Captioning model and releasing resources")
    settings.IC_MODEL.clear()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


root_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@root_router.get("/")
def home(request: Request):
    return templates.TemplateResponse("ic_form.html", {"request": request})


@root_router.post("/caption")
def caption(request: Request, image: UploadFile = File()):
    data = image.file.read()
    caption = ''
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(data)
        caption = settings.IC_MODEL[0].caption(tmp.name)
    image.file.close()

    # encoding and decoding the image bytes
    encoded_image = base64.b64encode(data).decode("utf-8")

    return templates.TemplateResponse(
        "ic_form.html", {"request": request,  "img": encoded_image, "caption": caption})


app.include_router(root_router)
#app.include_router(api_router, prefix=settings.API_V1_STR)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
