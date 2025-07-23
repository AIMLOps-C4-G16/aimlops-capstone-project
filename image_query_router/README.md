# 🖼️ Image Processing API

This service provides multiple capabilities for processing and managing images, such as:

- Generating **captions** for images
- Finding **similar** or **matching** images
- **Indexing** images for future reference
- **Retrieving** images by their ID

---

## 🚀 API Endpoints

### 1. **POST** `/process/`

Processes the uploaded image based on the operation specified by the `query` parameter.

#### 📤 Request

- **Content Type**: `multipart/form-data`
- **Parameters**:

| Name   | Type   | Required | Description                                                        |
|--------|--------|----------|--------------------------------------------------------------------|
| query  | string | ✅       | Operation to perform. Options: `caption`, `search`, `similar`, `index` |
| files  | file   | ✅       | The image file to be processed                                     |

#### 📥 Example

```bash
curl --location 'http://localhost:8000/process/' \
--form 'query="index"' \
--form 'files=@"/path/to/image.jpg"'
```


📬 Response Examples
```
✅ query=caption

{
  "result": {
    "caption": [
      "The image shows a group of women wearing traditional clothing, with their faces blurred out. They are dressed in vibrant, striped skirts and tops, with red and yellow accents. The background appears to be a mountainous landscape."
    ]
  }
}
```

✅ query=similar

```
{
  "result": {
    "similar_images": [
      "34d2b691-1623-4ee2-bc3f-e3d29b828990",
      "ce252c44-6fe2-4fc0-9197-bb785cab114b",
      "d247a6dd-6321-4702-b85a-7522a50f990b"
    ]
  }
}

```
✅ query=search

```
{
  "result": {
    "search_images": [
      "1792bf6a-4670-4683-96e5-8a1c28932f33",
      "5de4ed69-ac6c-4862-92ee-ea5bd3361306",
      "63d062a6-716a-42fa-a07d-3b9c0c1d347b"
    ]
  }
}
```

✅ query=index

```
{
  "result": {
    "index_response": "Successfully indexed 1 new images in the user image database"
  }
}

```

2. GET /image/{image_id}

Retrieves the image file corresponding to the given image_id.

```
curl --location 'http://localhost:8080/image/afdf6e9b-1fcb-4627-9729-deb71555feed'

```