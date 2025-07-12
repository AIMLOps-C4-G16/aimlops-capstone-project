import base64
import tempfile

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.templating import Jinja2Templates

from config import settings


captioning_router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIRECTORY)


@captioning_router.get("/caption")
def home(request: Request):
    return templates.TemplateResponse("ic_form.html", {"request": request})


@captioning_router.post("/caption")
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
