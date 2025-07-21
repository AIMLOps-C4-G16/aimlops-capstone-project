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
import asyncio
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
INDEX_API_URL = os.getenv("INDEX_API_URL")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

MENU_MESSAGE = (
    "🌟 What is your next action?\n\n"
    "1️⃣ *Image Captioning* (Upload an image)\n"
    "2️⃣ *Image Search* (Send text to get images)\n"
    "3️⃣ *Similar Images* (Send image + count)\n"
    "4️⃣ *Image Indexing* (Upload multiple images)\n\n"
    "👉 Reply with the option number (1, 2, 3, or 4) to continue."
)



@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(request: Request):
    form = await request.form()
    from_number_raw = form.get("From", "")
    from_number = from_number_raw.strip().lower()
    num_media = int(form.get("NumMedia", 0))
    body_text = form.get("Body", "").strip().lower()  # 👈 normalize for consistent matching
    response_texts = []

    print(f"📥 Incoming message from {from_number}: {body_text} (NumMedia: {num_media})")

    if num_media > 0 and session_state.get(from_number, {}).get("step") == "awaiting_option":
        # If user sends media while awaiting option, reset to menu
        session_state[from_number]["step"] = "menu"
        return send_whatsapp_message(from_number, MENU_MESSAGE)
# 1️⃣ Check if user is new or greeted
    if from_number not in session_state or body_text in ["hi", "hello", "hey", "start"] and num_media == 0:
        session_state[from_number] = {"step": "awaiting_option"}
        send_whatsapp_message(
            to=from_number,
            message=(
                    "🌟 Welcome to the Image Caption and Search Assistant!\n\n"
                    "1️⃣ *Image Captioning* (Upload an image)\n"
                    "2️⃣ *Image Search* (Send text to get images)\n"
                    "3️⃣ *Similar Images* (Send image + count)\n"
                    "4️⃣ *Image Indexing* (Upload multiple images)\n\n"
                    "👉 Reply with the option number (1, 2, 3, or 4) to continue."
            )
        )
        return
    
 
    #print(session_state[from_number]["step"])
    # 2️⃣ Handle user flow based on step
    print(f"🔎 User {from_number} step: {session_state.get(from_number, {}).get('step', 'unknown')}")
    user_state = session_state[from_number]

    if user_state["step"] == "menu":
      session_state[from_number]["step"] = "awaiting_option"
      return send_whatsapp_message(from_number, MENU_MESSAGE)

    if user_state["step"] == "awaiting_option" and num_media == 0:
        if body_text in ["1", "2", "3","4"]:
            user_state["option"] = body_text
            user_state["handled"] = False  # Reset handled state for new option
            if body_text == "1":
                user_state["step"] = "awaiting_image"
                send_whatsapp_message(to=from_number, message="📷 Great! Please upload an image. I’ll generate a caption for you.")
            elif body_text == "2":
                user_state["step"] = "awaiting_search_text"
                send_whatsapp_message(to=from_number, message="🔍 Nice choice! What would you like to search for? Type your keywords.")
            elif body_text == "3":
                user_state["step"] = "awaiting_image_for_similar"
                send_whatsapp_message(to=from_number, message="📷 Okay! Please upload an image.")
            elif body_text == "4":
                user_state["step"] = "awaiting_images_for_indexing"
                send_whatsapp_message(to=from_number, message="📤 Please upload *multiple images* to index.")
        else:
            send_whatsapp_message(to=from_number, message="❌ Invalid option. Please reply with 1, 2, 3, or 4.")
    
    elif user_state["step"] == "awaiting_images_for_indexing":
        if num_media > 0:
            if user_state.get("handled"):
                # Prevent duplicate processing from multiple webhook calls
             return
            try:
                image_files = []
                for i in range(num_media):
                    media_url = form.get(f"MediaUrl{i}")
                    content_type = form.get(f"MediaContentType{i}", "image/jpeg")

                    media_response = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
                    if media_response.status_code != 200:
                        continue

                    image_files.append(("images", (f"image{i}.jpg", media_response.content, content_type)))

                if not image_files:
                    send_whatsapp_message(to=from_number, message="⚠️ No valid images found.")
                else:
                    response = requests.post(INDEX_API_URL, files=image_files, timeout=30)

                    if response.status_code == 200:
                        send_whatsapp_message(to=from_number, message="✅ Images indexed successfully!")
                    else:
                        send_whatsapp_message(to=from_number, message=f"❌ Indexing failed: {response.status_code}")

            except Exception as e:
                send_whatsapp_message(to=from_number, message=f"❌ Error: {str(e)}")

            # ✅ Mark handled and reset flow
            user_state["handled"] = True
            # 🔄 Reset state only once after handling input
            session_state[from_number]["step"] = "awaiting_option"
            return send_whatsapp_message(to=from_number, message=MENU_MESSAGE)
            
        else:
            # This happens if WhatsApp sends an extra message without media
            return

    elif user_state["step"] == "awaiting_image" and num_media > 0:
        media_url = form.get("MediaUrl0")
        captions = await fetch_caption_from_file(media_url)  # Your existing logic
        send_whatsapp_message(to=from_number, message=f"🖼 Caption: {captions}")
        session_state[from_number]["step"] = "awaiting_option"
        return send_whatsapp_message(from_number, MENU_MESSAGE)
        #session_state.pop(from_number)

    elif user_state["step"] == "awaiting_search_text":
        user_state["search_text"] = body_text
        user_state["step"] = "awaiting_search_count"
        send_whatsapp_message(to=from_number, message="🔢 How many images would you like to receive? (e.g., 3)")

    elif user_state["step"] == "awaiting_search_count":
      try:
        count = int(body_text)
        search_text = user_state["search_text"]

        send_whatsapp_message(to=from_number, message=f"🔍 Searching for *{search_text}*...")

        search_urls = await new_perform_image_search(query=search_text, num=count)
        print(f"🔎 Search results for '{search_text}': {search_urls}")
        if search_urls:
            await new_send_images_on_whatsapp(to=from_number, image_urls=search_urls, query=search_text)
            #send_whatsapp_message(to=from_number, message=f"✅ Sent {len(search_urls)} images for '{search_text}'")
        else:
              send_whatsapp_message(to=from_number, message="⚠️ No images found.")

      except ValueError:
        send_whatsapp_message(to=from_number, message="❌ Please send a number like 3 or 5.")
       
      session_state[from_number]["step"] = "menu"
  
      #session_state.pop(from_number)
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

                    similar_urls = await new_perform_image_similarity_search(media_url, count)

                    if similar_urls:
                        await new_send_images_on_whatsapp(to=from_number, image_urls=similar_urls, query="Similar Image")
                    else:
                          send_whatsapp_message(to=from_number, message="⚠️ No similar images found.")

                except ValueError:
                    send_whatsapp_message(to=from_number, message="❌ Please send a valid number like 3 or 5.")
                    
                session_state[from_number]["step"] = "menu"
               # session_state.pop(from_number)

    else:
        if body_text:  # Only if there's actually unexpected text
            send_whatsapp_message(to=from_number, message="❓ I didn't understand that. Send 'Hi' to restart.")
        session_state.pop(from_number, None)
        return
    
    return #PlainTextResponse("Hi")

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

async def new_send_images_on_whatsapp(to: str, image_urls: list, query: str):
    """
    Sends groups of image URLs on WhatsApp, each group with a label.
    image_urls: List[List[str]] with 3 sublists [user images, flickr images, internet images]
    """

    source_labels = ["📤 User Images", "📷 Flickr Images", "🌐 Internet Images"]

    for group_idx, group in enumerate(image_urls):
        if not group:
            continue

        caption = source_labels[group_idx] + f" for *{query}*"
        for i, url in enumerate(group):
            
            try:
                if not url.startswith("http"):
                    print(f"❌ Skipping invalid URL: {url}")
                    continue

                twilio_client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=to,
                    body=caption if i == 0 else "",  # Only send caption for first image in each group
                    media_url=[url],
                )
                print(f"✅ Sent image {i+1} from group {group_idx+1}")
                
            except Exception as e:
                print(f"❌ Error sending image {i+1} in group {group_idx+1}: {e}")




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

async def new_perform_image_search(query: str, num: int):
    try:
        response = requests.post(
            SEARCH_API_URL,
            data={"text": query, "num": num},
            timeout=30,
        )
        if response.status_code != 200:
            print(f"❌ Search API HTTP Error {response.status_code}")
            return []

        raw_data = response.json()  # expected: [[user], [flickr], [internet]]
        if not isinstance(raw_data, list) or not all(isinstance(i, list) for i in raw_data):
            print("❌ Invalid format from Search API")
            return []

        categorized_urls = []

        for source_list in raw_data:
            urls = []
            for base64_str in source_list:
                try:
                    image_bytes = base64.b64decode(base64_str)
                    mimetype = "image/jpeg"
                    img_id = str(uuid4())
                    image_store[img_id] = (image_bytes, mimetype)
                    public_url = f"{PUBLIC_BASE_URL}/image/{img_id}"
                    urls.append(public_url)
                except Exception as e:
                    print(f"❌ Error decoding base64 image: {e}")
            categorized_urls.append(urls)

        return categorized_urls  # list of 3 URL lists

    except Exception as e:
        print(f"❌ perform_image_search error: {e}")
        return []

async def new_perform_image_similarity_search(image_url: str, num: int):
    try:
        print(f"📥 Downloading image from WhatsApp: {image_url}")
        image_response = requests.get(image_url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))

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

        raw_data = response.json()  # expected: [["user_imgs"], ["flickrdb_imgs"], ["internet_imgs"]]
        if not isinstance(raw_data, list) or not all(isinstance(group, list) for group in raw_data):
            print("❌ Unexpected format from similarity API")
            return []

        categorized_urls = []

        for group_index, group in enumerate(raw_data):
            urls = []
            for i, base64_str in enumerate(group):
                try:
                    image_bytes = base64.b64decode(base64_str)
                    mimetype = "image/jpeg"
                    img_id = str(uuid4())
                    image_store[img_id] = (image_bytes, mimetype)

                    public_url = f"{PUBLIC_BASE_URL}/image/{img_id}"
                    urls.append(public_url)
                    print(f"🖼️ Stored Similar Image {i+1} from group {group_index + 1}: {public_url}")
                except Exception as e:
                    print(f"❌ Error decoding image {i+1} in group {group_index + 1}: {e}")
            categorized_urls.append(urls)

        return categorized_urls

    except Exception as e:
        print(f"❌ perform_image_similarity_search error: {e}")
        return []

async def upload_images_to_index_api(media_urls: list) -> str:
    try:
        files = []
        for i, url in enumerate(media_urls):
            resp = requests.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
            if resp.status_code != 200:
                return f"❌ Failed to download image {i+1}."
            files.append(('images', (f'image_{i+1}.jpg', resp.content, 'image/jpeg')))

        index_response = requests.post(
            INDEX_API_URL,  # Set INDEX_API_URL in .env
            files=files,
            timeout=30
        )

        if index_response.status_code == 200:
            return "✅ Images indexed successfully!"
        else:
            return f"❌ Indexing failed: {index_response.text}"

    except Exception as e:
        return f"❌ Exception during indexing: {str(e)}"
