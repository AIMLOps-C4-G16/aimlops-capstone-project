from cachetools import TTLCache
from uuid import uuid4
import base64
import requests
from langchain.tools import tool
from utils.image_store import store_image
import os


host = os.environ.get("IMAGE_SERVICE_HOST")

SEARCH_API_URL = f"{host}/search"

@tool(return_direct=True)
def search_image_by_text_tool(query: str) -> list:
    """Search images by text using the Search API and return categorized public URLs."""

    try:
        response = requests.post(
            SEARCH_API_URL,
            data={"text": query},
            timeout=30,
        )

        if response.status_code != 200:
            print(f"❌ Search API HTTP Error {response.status_code}")
            return []

        raw_data = response.json()
        if not isinstance(raw_data, list) or not all(isinstance(i, list) for i in raw_data):
            print("❌ Invalid format from Search API")
            return []

        categorized_urls = []
        print(f"✅ Found {len(raw_data)} categories.")

        for source_list in raw_data:
            print(f"✅ Found {len(source_list)} categories.")
            for base64_str in source_list:
                try:
                    image_bytes = base64.b64decode(base64_str)
                    mimetype = "image/jpeg"
                    img_id = store_image(image_bytes) 
                    categorized_urls.append(img_id)
                except Exception as e:
                    print(f"❌ Error decoding base64 image: {e}")
        print(f"✅ Found {categorized_urls} categories with images.")
        result = {
            "search_images": categorized_urls
        }
        return result

    except Exception as e:
        print(f"❌ search_image_by_text_tool error: {e}")
        return []
