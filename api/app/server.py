from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
import base64
import tempfile

from app import __version__, schemas
from inference import generate_caption

PROJECT_NAME = 'Image Captioning API'

api = FastAPI()

templates = Jinja2Templates(directory="templates")

@api.get("/")
def dynamic_file(request: Request):
    return templates.TemplateResponse("dynamic.html", {"request": request})

@api.get("/health", response_model=schemas.Health, status_code=200)
def health() -> dict:
    health = schemas.Health(
        name=PROJECT_NAME, api_version=__version__, model_name='', model_status=''
    )
    return health.model_dump()

@api.post("/dynamic")
def dynamic(request: Request, file: UploadFile = File()):
    data = file.file.read()
    caption = ''
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(data)
        caption = generate_caption(tmp.name)
    file.file.close()

    # encoding and decoding the image bytes
    encoded_image = base64.b64encode(data).decode("utf-8")

    return templates.TemplateResponse(
        "dynamic.html", {"request": request,  "img": encoded_image, "caption": caption})