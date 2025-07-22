from langchain.tools import tool
import requests
import mimetypes
import os

host = os.environ.get("IMAGE_SERVICE_HOST")

CAPTION_API_URL = f"{host}/caption"


@tool(return_direct=True)
def caption_image_tool(image_path: str) -> str:
    """Send an image file to the captioning API and return the generated caption."""
        

    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(image_path)
    mime_type = mime_type or 'application/octet-stream'

    headers = {
        'accept': 'application/json'
    }

    try:
        with open(image_path, 'rb') as img_file:
            files = {
                'image': (image_path, img_file, mime_type)
            }

            response = requests.post(CAPTION_API_URL, headers=headers, files=files)
            response.raise_for_status()
            result = response.json()
            print(f"Caption response: {result}")
    except Exception as e:
        caption = f"[Error] Failed to get caption: {str(e)}"

    return result
