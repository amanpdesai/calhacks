import os
import openai
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# Set your API key
openai.api_key = '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'

def get_in_depth_summary(caption):
    prompt = f"Provide a thorough and detailed analysis, including possible contexts, emotions, and implications, based on the following image description:\n\n'{caption}'"
    response = openai.ChatCompletion.create(
        engine='gpt-4o',
        prompt=prompt,
        max_tokens = 500,
        temperature=0.7,
        n=1,
        stop=None
    )
    summary = response['choices'][0]['text'].strip()
    return summary

try:
    # Load and process the image
    image_path = os.path.join('images', 'pfp.png')
    image = Image.open(image_path).convert('RGB')

    # Generate a caption using BLIP
    processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
    model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
    inputs = processor(image, return_tensors='pt')

    with torch.no_grad():
        out = model.generate(**inputs, max_length = 50)
        caption = processor.decode(out[0], skip_special_tokens=True)
        print(f"Generated Caption: {caption}")

    # Get an in-depth summary from OpenAI
    summary = get_in_depth_summary(caption)
    print(f"\nIn-Depth Summary:\n{summary}")

except Exception as e:
    print(f"An error occurred: {e}")