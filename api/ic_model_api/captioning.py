import base64
import tempfile

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.templating import Jinja2Templates

from config import settings


captioning_router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIRECTORY)


def process_image(image: UploadFile):
    data = image.file.read()
    caption = ''
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(data)
        caption = settings.IC_MODEL[0].caption(tmp.name)
    image.file.close()

    return data, caption


@captioning_router.post("/caption")
def caption(request: Request, image: UploadFile = File()):
    _, caption = process_image(image)
    return [caption]


@captioning_router.get("/caption_page")
def home(request: Request):
    return templates.TemplateResponse("ic_form.html", {"request": request})


@captioning_router.post("/caption_page")
def caption_page(request: Request, image: UploadFile = File()):
    data, caption = process_image(image)

    # encoding and decoding the image bytes
    encoded_image = base64.b64encode(data).decode("utf-8")

    return templates.TemplateResponse(
        "ic_form.html", {"request": request,  "img": encoded_image, "caption": caption})
