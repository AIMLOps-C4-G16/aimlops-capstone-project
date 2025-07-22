from cachetools import TTLCache
from uuid import uuid4
from typing import Optional, Tuple

# Create a TTL cache: max 100 images, 5 min expiration
_cache = TTLCache(maxsize=100, ttl=600)

def store_image(image_bytes: bytes, mimetype: str = "image/jpeg") -> str:
    """Store an image in the cache and return a unique image ID."""
    img_id = str(uuid4())
    _cache[img_id] = (image_bytes, mimetype)
    return img_id

def get_image(img_id: str) -> Optional[Tuple[bytes, str]]:
    """Retrieve an image and its mimetype by ID, or return None if not found."""
    return _cache.get(img_id)
