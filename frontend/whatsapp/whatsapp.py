import os
import base64
from io import BytesIO
from uuid import uuid4
import requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, StreamingResponse
from dotenv import load_dotenv
from twilio.rest import Client
from requests.auth import HTTPBasicAuth
# In-memory store for served images
image_store = {}
session_state = {}
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
# 1️⃣ Check if user is new or greeted
    if from_number not in session_state or body_text in ["hi", "hello", "hey", "start"]:
        session_state[from_number] = {"step": "awaiting_option"}
        send_whatsapp_message(
            to=from_number,
            message=(
                "👋 *Welcome!*\n\nI can help you with the following:\n\n"
                "1️⃣ *Image Captioning* (Upload an image)\n"
                "2️⃣ *Image Search* (Send text to get images)\n"
                "3️⃣ *Similar Images* (Send image + count)\n\n"
                "👉 Reply with the option number (1, 2, or 3) to continue."
            )
        )
        return PlainTextResponse("OK")

    # 2️⃣ Handle user flow based on step
    user_state = session_state[from_number]

    if user_state["step"] == "awaiting_option":
        if body_text in ["1", "2", "3"]:
            user_state["option"] = body_text
            if body_text == "1":
                user_state["step"] = "awaiting_image"
                send_whatsapp_message(to=from_number, message="📷 Please upload an image for captioning.")
            elif body_text == "2":
                user_state["step"] = "awaiting_search_text"
                send_whatsapp_message(to=from_number, message="🔍 Please enter keywords to search for images.")
            elif body_text == "3":
                user_state["step"] = "awaiting_image_for_similar"
                send_whatsapp_message(to=from_number, message="📷 Upload an image and tell me how many similar images you want (e.g., `3`).")
        else:
            send_whatsapp_message(to=from_number, message="❌ Invalid option. Please reply with 1, 2, or 3.")

    elif user_state["step"] == "awaiting_image" and num_media > 0:
        media_url = form.get("MediaUrl0")
        captions = await fetch_caption_from_file(media_url)  # Your existing logic
        send_whatsapp_message(to=from_number, message=f"🖼 Caption: {captions}")
        session_state.pop(from_number)

    elif user_state["step"] == "awaiting_search_text":
        user_state["search_text"] = body_text
        user_state["step"] = "awaiting_search_count"
        send_whatsapp_message(to=from_number, message="🔢 How many images would you like to receive? (e.g., 3)")
        # search_urls = await perform_image_search(query=body_text, num=3)
        # send_images_on_whatsapp(to=from_number, image_urls=search_urls, query=body_text)
        # session_state.pop(from_number)
    elif user_state["step"] == "awaiting_search_count":
      try:
        count = int(body_text)
        search_text = user_state["search_text"]

        send_whatsapp_message(to=from_number, message=f"🔍 Searching for *{search_text}*...")

        search_urls = await perform_image_search(query=search_text, num=count)

        if search_urls:
            send_images_on_whatsapp(to=from_number, image_urls=search_urls, query=search_text)
            send_whatsapp_message(to=from_number, message=f"✅ Sent {len(search_urls)} images for '{search_text}'")
        else:
            send_whatsapp_message(to=from_number, message="⚠️ No images found.")

      except ValueError:
        send_whatsapp_message(to=from_number, message="❌ Please send a number like 3 or 5.")

      session_state.pop(from_number)
    elif user_state["step"] == "awaiting_image_for_similar" and num_media > 0:
        # Save uploaded image URL and ask for count
        media_url = form.get("MediaUrl0")
        user_state["media_url"] = media_url
        user_state["step"] = "awaiting_similar_count"

        send_whatsapp_message(to=from_number, message="🔢 How many similar images would you like? (e.g., 3)")

    elif user_state["step"] == "awaiting_similar_count":
                try:
                    count = int(body_text)
                    media_url = user_state.get("media_url")

                    if not media_url:
                        raise ValueError("Image URL missing")

                    send_whatsapp_message(to=from_number, message="🔍 Searching for similar images...")

                    similar_urls = await perform_image_similarity_search(media_url, count)

                    if similar_urls:
                        send_images_on_whatsapp(to=from_number, image_urls=similar_urls, query="Similar Image")
                        send_whatsapp_message(to=from_number, message=f"✅ Sent {len(similar_urls)} similar images.")
                    else:
                        send_whatsapp_message(to=from_number, message="⚠️ No similar images found.")

                except ValueError:
                    send_whatsapp_message(to=from_number, message="❌ Please send a valid number like 3 or 5.")

                session_state.pop(from_number)

    # elif user_state["step"] == "awaiting_image_for_similar" and num_media > 0:
    #     try:
    #         # parse num from earlier message or default
    #         num = int(''.join(filter(str.isdigit, body_text))) or 3
    #     except:
    #         num = 3
    #     media_url = form.get("MediaUrl0")
    #     sim_urls = await perform_image_similarity_search(media_url, num)
    #     send_images_on_whatsapp(to=from_number, image_urls=sim_urls, query="Similar")
    #     session_state.pop(from_number)

    else:
        send_whatsapp_message(to=from_number, message="❓ I didn't understand that. Send 'Hi' to restart.")
        session_state.pop(from_number, None)

    return PlainTextResponse("OK")

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

        raw_data = response.json()  #[["base64img1", "base64img2"]]
        if not isinstance(raw_data, list):
            print("❌ Search API returned invalid format")
            return []
        images_nested = raw_data[0] if isinstance(raw_data, list) and len(raw_data) > 0 else []

        urls = []

        for i, base64_str in enumerate(images_nested):
            try:
                image_bytes = base64.b64decode(base64_str)
                mimetype = "image/jpeg"
                img_id = str(uuid4())
                image_store[img_id] = (image_bytes, mimetype)

                public_url = f"{PUBLIC_BASE_URL}/image/{img_id}"
                urls.append(public_url)
                print(f"🖼️ Stored Image {i+1}: {public_url}")

            except Exception as e:
                print(f"❌ Error decoding image {i+1}: {e}")

        return urls

    except Exception as e:
        print(f"❌ perform_image_search error: {e}")
        return []


async def perform_image_similarity_search(image_url: str, num: int):
    try:
        print(f"📥 Downloading image from WhatsApp: {image_url}")
        image_response = requests.get(image_url,auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))

        if image_response.status_code != 200:
            print(f"❌ Failed to download image: {image_response.status_code}")
            return []

        image_file = ("image.jpg", image_response.content, "image/jpeg")

        response = requests.post(
            SEARCH_SIMILAR_API_URL,
            files={"image": image_file},
            data={"num": str(num)},
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ API error {response.status_code}: {response.text}")
            return []

        raw_data = response.json()  # expected: [["base64img1", "base64img2"]]
        images_nested = raw_data[0] if isinstance(raw_data, list) and len(raw_data) > 0 else []

        urls = []

        for i, base64_str in enumerate(images_nested):
            try:
                image_bytes = base64.b64decode(base64_str)
                mimetype = "image/jpeg"
                img_id = str(uuid4())
                image_store[img_id] = (image_bytes, mimetype)

                public_url = f"{PUBLIC_BASE_URL}/image/{img_id}"
                urls.append(public_url)
                print(f"🖼️ Stored Similar Image {i+1}: {public_url}")

            except Exception as e:
                print(f"❌ Error decoding similar image {i+1}: {e}")

        return urls

    except Exception as e:
        print(f"❌ perform_image_similarity_search error: {e}")
        return []
def generate_friendly_prompt(option_number):
    if option_number == "1":
        return "Great! Please upload an image. I’ll generate a caption for you."
    elif option_number == "2":
        return "Nice choice! What would you like to search for? Type your keywords."
    elif option_number == "3":
        return "Okay! Please upload an image and tell me how many similar ones you want."
