import tempfile
from typing import Annotated

from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates

from config import settings


search_router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIRECTORY)


def caption_image(image: UploadFile):
    caption = ''
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(image.file.read())
        image.file.close()
        caption = settings.IC_MODEL[0].caption(tmp.name)
    return caption


@search_router.post("/search")
def search(request: Request, text: Annotated[str, Form()], num: Annotated[int, Form()] = 3):
    return settings.IMAGE_DB_INDEX[0].search(text, num)


@search_router.get("/search_page")
def search_home(request: Request):
    return templates.TemplateResponse("search_form.html", {"request": request})


@search_router.post("/search_page")
def search_page(request: Request, text: Annotated[str, Form()], num: Annotated[int, Form()] = 3):
    imgs_list = settings.IMAGE_DB_INDEX[0].search(text, num)
    return templates.TemplateResponse(
        "search_form.html", {"request": request,  "imgs_list": imgs_list})


@search_router.post("/search_similar")
def search_similar(request: Request, image: UploadFile = File(), num: Annotated[int, Form()] = 3):
    caption = caption_image(image)
    return settings.IMAGE_DB_INDEX[0].search(caption, num)


@search_router.get("/search_similar_page")
def search_similar_home(request: Request):
    return templates.TemplateResponse("search_similar_form.html", {"request": request})


@search_router.post("/search_similar_page")
def search_similar_page(request: Request, image: UploadFile = File(), num: Annotated[int, Form()] = 3):
    caption = caption_image(image)
    imgs_list = settings.IMAGE_DB_INDEX[0].search(caption, num)
    return templates.TemplateResponse(
        "search_similar_form.html", {"request": request,  "imgs_list": imgs_list, "caption": caption})
