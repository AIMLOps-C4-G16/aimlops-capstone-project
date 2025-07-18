import os
import base64
from io import BytesIO
from uuid import uuid4
import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from dotenv import load_dotenv
from twilio.rest import Client
# In-memory store for served images
image_store = {}
load_dotenv()
# Define CORS settings
origins = ["*"]  # Allow requests from any origin
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "WhatsApp captioning webhook online"}
# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Your Captioning API
IMAGE_API_URL = os.getenv("IMAGE_API_URL")
SEARCH_API_URL = os.getenv("SEARCH_API_URL")  # e.g., https://abc.loca.lt/search
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL") # e.g., https://abc.loca.lt
SEARCH_SIMILAR_API_URL = os.getenv("SEARCH_SIMILAR_API_URL")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

#@app.post("/whatsapp")
@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(request: Request):
    form = await request.form()
    from_number = form.get("From")
    num_media = int(form.get("NumMedia", 0))
    body_text = form.get("Body", "").strip()
    response_texts = []

    if num_media > 0:
        for i in range(num_media):
            media_url = form.get(f"MediaUrl{i}")
            media_type = form.get(f"MediaContentType{i}")

            caption = await fetch_caption_from_file(media_url)
            response_texts.append(f"🖼 Caption {i+1}: {caption}")
    elif body_text:
        # Perform image search based on text
        search_term, num_images = parse_search_command(body_text)
        image_urls = await perform_image_search(search_term, num_images)
        print(f"🔎 Found {len(image_urls)} image(s) for '{search_term}'")
        if image_urls:
            send_images_on_whatsapp(to=from_number, image_urls=image_urls, query=search_term)
            send_whatsapp_message(to=from_number, message=f"✅ Sent {len(image_urls)} image(s) for '{search_term}'")
        else:
            send_whatsapp_message(to=from_number, message="⚠️ No images found or an error occurred during search.")
    
    elif num_media > 0 and body_text.lower().startswith("similar"):
    # Example body: "similar 3"
     try:
        _, num = body_text.strip().split()
        num = int(num)
     except:
        num = 3  # fallback

        media_urls = [
            form.get(f"MediaUrl{i}") for i in range(num_media)
        ]

        for media_url in media_urls:
            similar_urls = await perform_image_similarity_search(media_url, num)
            print(f"🔍 Found {len(similar_urls)} similar image(s) for {media_url}")
            if similar_urls:
                send_images_on_whatsapp(to=from_number, image_urls=similar_urls, query="Similar Image")
            else:
                send_whatsapp_message(to=from_number, message="⚠️ No similar images found.")

    else:
        response_texts.append("❌ No image received. Please send image(s) to generate captions.")

    if response_texts:
        full_response = "\n".join(response_texts).strip()
        if full_response:
            send_whatsapp_message(to=from_number, message=full_response)
        else:
            print("⚠️ Skipping empty message to Twilio")
    else:
        send_whatsapp_message(to=from_number, message="❌ No content to send.")
    return "OK"

@app.get("/image/{img_id}")
def serve_image(img_id: str):
    if img_id not in image_store:
        return {"error": "Image not found"}
    image_bytes, mimetype = image_store[img_id]
    return StreamingResponse(BytesIO(image_bytes), media_type=mimetype)

def send_whatsapp_message(to: str, message: str):
    twilio_client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to,
    )

# 📤 Send multiple WhatsApp image messages
def send_images_on_whatsapp(to: str, image_urls: list, query: str):
    for i, img_url in enumerate(image_urls):
        print(f"🔎 Sending image URL to Twilio: {img_url}")
        if not img_url.startswith("https://"):
            print(f"❌ Skipping invalid URL: {img_url}")
            continue
        caption = f"🔍 Result {i+1} for '{query}'"
        try:
            twilio_client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                to=to,
                body=caption,
                media_url=[img_url],
            )
        except Exception as e:
            print(f"❌ Error sending image {i+1}: {e}")

async def fetch_caption_from_file(media_url: str) -> str:
    print(f"🔎 Fetching caption for media URL: {media_url}")
    try:
        # Download image from Twilio CDN
        media_response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        if media_response.status_code != 200:
            return f"❌ Error downloading image: {media_response.status_code}"

        # Send image as file to captioning API
        files = {
            'image': ('uploaded.jpg', media_response.content, 'image/jpeg'),
        }
        response = requests.post(
            IMAGE_API_URL,
            files=files,
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data[0] if len(data) > 0 else "No caption returned."
            elif isinstance(data, dict):
                return data.get("caption", "No caption returned.")
            else:
                return "Unexpected response format from captioning API."
        else:
            return f"❌ Captioning API Error: {response.status_code}"
    except Exception as e:
        return f"❌ Exception: {str(e)}"


# 🧠 Parse search string like "cake 5" or "temple"
def parse_search_command(text: str):
    parts = text.strip().split()
    if len(parts) >= 2 and parts[-1].isdigit():
        return " ".join(parts[:-1]), int(parts[-1])
    else:
        return text, 3  # Default to 1 image


async def perform_image_search(query: str, num: int):
    try:
        response = requests.post(
            SEARCH_API_URL,
            data={"text": query, "num": num},
            timeout=15,
        )
        if response.status_code != 200:
            print(f"❌ Search API HTTP Error {response.status_code}")
            return []

        base64_images = response.json()  # [['base64data'], ['base64data'], ...]

        urls = []

        for item in base64_images:
            if not isinstance(item, list) or not item:
                continue

            base64_str = item[0]  # unwrap the list

            if not isinstance(base64_str, str):
                continue

            try:
                image_bytes = base64.b64decode(base64_str)
                mimetype = "image/jpeg"  # Assume JPEG

                img_id = str(uuid4())
                image_store[img_id] = (image_bytes, mimetype)

                public_url = f"{PUBLIC_BASE_URL}/image/{img_id}"
                urls.append(public_url)

            except Exception as e:
                print(f"❌ Failed to decode image: {e}")
                continue

        return urls

    except Exception as e:
        print(f"❌ Search error: {e}")
        return []


async def perform_image_similarity_search(image_url: str, num: int):
    try:
        print(f"📤 Downloading image from WhatsApp URL: {image_url}")
        image_response = requests.get(image_url)

        if image_response.status_code != 200:
            print(f"❌ Failed to download image from WhatsApp: {image_response.status_code}")
            return []

        # Prepare the file as bytes
        image_file = ("image.jpg", image_response.content, "image/jpeg")

        print(f"🔍 Sending image to /search_similar with num={num}")
        response = requests.post(
            SEARCH_SIMILAR_API_URL,
            files={"image": image_file},
            data={"num": str(num)},
            timeout=30,
        )

        if response.status_code != 200:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return []

        result = response.json()
        images = result.get("images", [])

        urls = []
        for i, img_obj in enumerate(images):
            base64_str = img_obj.get("data") if isinstance(img_obj, dict) else img_obj[0]
            if not base64_str:
                continue

            try:
                image_bytes = base64.b64decode(base64_str)
                mimetype = "image/jpeg"

                img_id = str(uuid4())
                image_store[img_id] = (image_bytes, mimetype)

                public_url = f"{PUBLIC_BASE_URL}/image/{img_id}"
                urls.append(public_url)

                print(f"✅ Similar Image {i+1} hosted at: {public_url}")

            except Exception as e:
                print(f"❌ Failed to decode image {i+1}: {e}")

        return urls

    except Exception as e:
        print(f"❌ Similarity Search error: {e}")
        return []
