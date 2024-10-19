import os
import openai
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import requests
import base64

# Set your API key
openai.api_key = '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'
client = openai.OpenAI(
    api_key=openai.api_key
)
serber = "http://localhost:5000/"
img_type = "image/png"

def download_frame(img_name):
    # URL of the Flask server's grab-frame endpoint
    url = serber + 'grab-frame'
    
    # Make a GET request to the grab-frame endpoint
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Save the content as an image file
        with open(img_name, 'wb') as f:
            f.write(response.content)
        print(f"Frame downloaded successfully as \'{img_name}\'")
    else:
        print(f"Failed to download frame. Status code: {response.status_code}")

def get_in_depth_summary(image_path):
    prompt = "Describe in detail everything that is visible in the image provided. Include all objects, people, and background elements. Mention the types of objects, their colors, positions, and any noticeable features or activities. If there are any brands, logos, or text, include those as well. Describe the setting, such as the type of location or event, and any other context that can be inferred. Be thorough and list as many elements as possible, even if they seem small or insignificant."

    with open(image_path, "rb") as image_file:
        img_data = image_file.read()
        img_b64_str = base64.b64encode(img_data).decode('utf-8')

    # Open the image file in binary mode
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{img_type};base64,{img_b64_str}"},
                    },
                ],
            }
        ],
    )

    # Extract the generated description from the response
    summary = response.choices[0].message.content
    return summary

def generate_full_summary():

    try:
        img_name = 'pfp.png'
        # Download image from serber
        os.chdir(os.getcwd() + '/server/images')
        download_frame(img_name)
        os.chdir('..')

        # Load and process the image
        image_path = os.path.join('server/images', img_name)

        # Get an in-depth summary from OpenAI
        summary = get_in_depth_summary(image_path)
        print(f"\nIn-Depth Summary:\n{summary}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    generate_full_summary()

if __name__ == "__main__":
    main()