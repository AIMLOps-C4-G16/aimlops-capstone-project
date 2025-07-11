import torch
import PIL

from unsloth import FastLanguageModel


class ICModel:


    def __init__(self):
        self.name = "unsloth/Llama-3.2-11B-Vision-Instruct"

        if torch.cuda.is_available():
            # Load tokenizer and model
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.name,
                max_seq_length=2048,
                load_in_4bit=True
            )

            FastLanguageModel.for_inference(self.model)
            self.status = "Model loaded"

            self.messages = [
                {"role": "user", "content": [
                    {"type": "image"},
                    {"type": "text", "text": "In a short sentence, briefly describe what you see in this image."}
                ]}
            ]
        
        else:
            self.status = "Unable to load model: CUDA not available"


    def caption(self, image_file):
        if self.status != "Model loaded":
            return self.status
        
        try:
            image = PIL.Image.open(image_file)

            input_text = self.tokenizer.apply_chat_template(self.messages, add_generation_prompt=True)
            inputs = self.tokenizer(
                image,
                input_text,
                add_special_tokens = False,
                return_tensors = "pt",
            ).to("cuda")

            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.8, top_p=0.9)
                return self.tokenizer.decode(outputs[0]).split('assistant<|end_header_id|>')[1].split('<|eot_id|>')[0]

        except Exception as e:
            raise str(e)
