import os
import torch
import PIL
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from unsloth import FastLanguageModel
from transformers import AutoTokenizer

MODEL_NAME = "unsloth/Llama-3.2-11B-Vision-Instruct"

# Load tokenizer and model
model, tokenizer = FastLanguageModel.from_pretrained(model_name=MODEL_NAME, max_seq_length=2048, load_in_4bit=True)

FastLanguageModel.for_inference(model)
device = "cuda" if torch.cuda.is_available() else "cpu"

instruction = "In a short sentence, briefly describe what you see in this image."

messages = [
    {"role": "user", "content": [
        {"type": "image"},
        {"type": "text", "text": instruction}
    ]}
]

def generate_caption(image_file):
    try:
        image = PIL.Image.open(image_file)

        input_text = tokenizer.apply_chat_template(messages, add_generation_prompt = True)
        inputs = tokenizer(
            image,
            input_text,
            add_special_tokens = False,
            return_tensors = "pt",
        ).to(device)

        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=160, do_sample=True, temperature=0.8, top_p=0.9)
            return tokenizer.decode(outputs[0]).split('assistant<|end_header_id|>')[1].split('<|eot_id|>')[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
