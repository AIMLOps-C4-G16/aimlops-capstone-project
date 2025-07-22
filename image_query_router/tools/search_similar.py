import base64
import requests
from langchain.tools import tool
from utils.image_store import store_image
import os

host = os.environ.get("IMAGE_SERVICE_HOST")

SEARCH_SIMILAR_API_URL = f"{host}/search_similar"

@tool(return_direct=True)
def search_similar_image_tool(image_path: str, num: int = 3) -> list:
    """
    Search for similar images using a reference image.
    Takes an image file path and number of results to return.
    Returns a flat list of public image URLs.
    """

    try:
        with open(image_path, "rb") as image_file:
            files = {
                "image": (image_path, image_file, "image/jpeg")
            }
         
            headers = {
                "accept": "application/json"
            }

            response = requests.post(
                SEARCH_SIMILAR_API_URL,
                headers=headers,
                files=files,
                timeout=30
            )

        if response.status_code != 200:
            print(f"❌ API Error: Status code {response.status_code}")
            return []

        response_data = response.json()

        if not isinstance(response_data, list):
            print("❌ Unexpected response format")
            return []

        image_urls = []

        for source_list in response_data:
            for base64_str in source_list:
                try:
                    image_bytes = base64.b64decode(base64_str)
                    mimetype = "image/jpeg"
                    img_id = store_image(image_bytes) 
                    image_urls.append(img_id)
                except Exception as e:
                    print(f"❌ Error decoding base64 image: {e}")
        print(f"✅ Found {image_urls} categories with images.")
        return image_urls

    except Exception as err:
        print(f"❌ search_similar_image_tool failed: {err}")
        return []
