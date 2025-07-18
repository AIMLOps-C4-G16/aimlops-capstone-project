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
    
    image_files, captions = [], []
    for image in images:
        filename = f"{subfolder}/{randomword(16)}.jpg"
        with open(filename, "wb") as f:
            f.write(image.file.read())
        
        caption = settings.SHARED["IC_MODEL"].caption(filename)

        image_files.append(filename)
        captions.append(caption)
    
    settings.SHARED["IMAGE_DB_INDEX"].index(image_files, captions)


@indexing_router.post("/index")
def index(request: Request, images: List[UploadFile]):
    index_images(images)
    return f"Successfully indexed {len(images)} images"
