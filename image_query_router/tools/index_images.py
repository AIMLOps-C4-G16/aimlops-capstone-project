import base64
import requests
from typing import List
from langchain.tools import tool
from utils.image_store import store_image
import os


host = os.environ.get("IMAGE_SERVICE_HOST")

INDEX_API_URL = f"{host}/index"

@tool(return_direct=True)
def index_images_to_the_stores(image_paths: List[str]) -> List[str]:
    """
    Index a list of images to the store.
    Takes a list of image file paths.
    Returns a list of public image URLs (or identifiers).
    """

    try:
        files = []

        for path in image_paths:
            try:
                f = open(path, "rb")
                files.append(("images", (path, f, "image/jpeg")))
            except Exception as e:
                print(f"❌ Failed to open {path}: {e}")

        if not files:
            print("❌ No valid images to upload.")
            return []

        headers = {
            "accept": "application/json"
        }

        response = requests.post(
            INDEX_API_URL,
            headers=headers,
            files=files,
            timeout=30
        )

        # Close all files to avoid resource leaks
        for _, (filename, file_obj, _) in files:
            file_obj.close()

        if response.status_code != 200:
            print(f"❌ API Error: Status code {response.status_code}")
            return []

        response_data = response.json()
        result = {
           "index_response": response_data
        }
        return result

    except Exception as err:
        print(f"❌ index_images_to_the_stores failed: {err}")
        return []
