from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional, List
import uuid
import shutil
import os
from agent.agent_router import agent  
from utils.image_store import get_image
from fastapi.responses import Response

app = FastAPI()

@app.post("/process/")
async def process(
    query: str = Form(...),
    files: Optional[List[UploadFile]] = File(None)
):    
    temp_file_paths = []

    try:
        # Save uploaded images to temp files
        if files:
            for file in files:
                temp_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                temp_file_paths.append(temp_path)

        # Format the input prompt for the agent
        image_list_section = ""
        if temp_file_paths:
            image_list_section = "\n".join(
                [f"Image {i+1}: {path}" for i, path in enumerate(temp_file_paths)]
            )

        prompt = f"""
You are an intelligent assistant capable of interpreting a user query and working with one or more images.

User Query: {query}

Uploaded Image Paths:
{image_list_section or 'No images provided.'}

Choose the correct action (like indexing or searching), and call the appropriate tool with relevant images.
"""

        # Call the agent with this full context
        result = agent.run(prompt)

        return {"result": result}

    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Processing failed: {err}")

    finally:
        # Clean up
        for path in temp_file_paths:
            if os.path.exists(path):
                os.remove(path)



@app.get("/image/{img_id}")
def get_image_route(img_id: str):
    result = get_image(img_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Image not found or expired")

    image_bytes, mimetype = result
    return Response(content=image_bytes, media_type=mimetype)