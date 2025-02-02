from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image
import torch

class VisionModel:
    def __init__(self, model_id="cafeai/SmolVLM-500M-Instruct"):
        # Initialize processor and model
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForVision2Seq.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16
        ).to("cuda").eval()  # Requires GPU with sufficient memory

    def describe_image(self, image_path, prompt="Describe the interface elements and actions shown in this screenshot"):
        try:
            # Load the image
            image = Image.open(image_path)
            
            # Create messages structure for the model
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                },
            ]

            # Process inputs using the processor
            inputs = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True
            )
            inputs = self.processor(images=image, text=inputs, return_tensors="pt")

            # Move inputs to GPU
            inputs = inputs.to("cuda")

            # Generate the response
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=500,
                    temperature=0.7,
                    do_sample=True
                )

            # Decode the generated tokens
            description = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]

            # Clear GPU memory
            torch.cuda.empty_cache()

            return description.strip()

        except Exception as e:
            return f"Error processing image: {str(e)}"