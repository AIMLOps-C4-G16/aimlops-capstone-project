from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
import base64

from inference import generate_caption

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def dynamic_file(request: Request):
    return templates.TemplateResponse("dynamic.html", {"request": request})

@app.post("/dynamic")
def dynamic(request: Request, file: UploadFile = File()):
    data = file.file.read()
    # Image will be saved in the uploads folder prefixed with uploaded_
    image_file = "uploads/saved_" + file.filename
    with open(image_file, "wb") as f:
        f.write(data)
    file.file.close()

    # encoding and decoding the image bytes
    encoded_image = base64.b64encode(data).decode("utf-8")
    caption = generate_caption(image_file)

    return templates.TemplateResponse(
        "dynamic.html", {"request": request,  "img": encoded_image, "caption": caption})