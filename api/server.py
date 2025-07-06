from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
import base64
import tempfile

from inference import generate_caption

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def dynamic_file(request: Request):
    return templates.TemplateResponse("dynamic.html", {"request": request})

@app.post("/dynamic")
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