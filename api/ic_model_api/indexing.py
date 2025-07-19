import base64
import os
import random
import string
from typing import List

from fastapi import APIRouter, Request, UploadFile
from fastapi.templating import Jinja2Templates

from config import settings


indexing_router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIRECTORY)


def randomword(length):
   letters = string.ascii_lowercase + string.digits
   return "".join(random.choice(letters) for _ in range(length))


def index_images(images: List[UploadFile]):
    # Create a new subfolder for every index request
    subfolder = settings.USER_IMAGE_DB_DIRECTORY + f"/{randomword(6)}"
    os.makedirs(subfolder)
    
    image_files, image_data, captions = [], [], []
    for image in images:
        filename = f"{subfolder}/{randomword(16)}.jpg"
        with open(filename, "wb") as f:
            data = image.file.read()
            f.write(data)
            image_data.append(base64.b64encode(data).decode("utf-8"))
        
        caption = settings.SHARED["IC_MODEL"].caption(filename)

        image_files.append(filename)
        captions.append(caption)
    
    msg = settings.SHARED["IMAGE_DB_INDEX"].index(image_files, captions)

    return list(zip(image_data, captions)), msg


@indexing_router.post("/index")
def index(request: Request, images: List[UploadFile]):
    _, msg = index_images(images)
    return msg


@indexing_router.get("/index_page")
def index_home(request: Request):
    return templates.TemplateResponse("index_form.html", {"request": request})


@indexing_router.post("/index_page")
def index_page(request: Request, images: List[UploadFile]):
    img_caption_pairs, msg = index_images(images)
    return templates.TemplateResponse(
        "index_form.html", {"request": request,  "img_caption_pairs": img_caption_pairs, "msg": msg})
