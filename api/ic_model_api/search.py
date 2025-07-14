import tempfile

from fastapi import APIRouter, Request, UploadFile, File

from config import settings


search_router = APIRouter()


def caption_image(image: UploadFile):
    caption = ''
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(image.file.read())
        image.file.close()
        caption = settings.IC_MODEL[0].caption(tmp.name)
    return caption


@search_router.get("/search")
def search(request: Request, text: str, num: int = 3):
    return settings.IMAGE_DB_INDEX[0].search(text, num)


@search_router.post("/search_similar")
def search_similar(request: Request, image: UploadFile = File(), num: int = 3):
    caption = caption_image(image)
    return settings.IMAGE_DB_INDEX[0].search(caption, num)
