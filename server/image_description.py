import os
from openai import OpenAI
from PIL import Image
import requests
import base64

# Set your API key
key = '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'
client = OpenAI(
    api_key=key
)

serber = "http://127.0.0.1:5000/"
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
    prompt = "Describe in detail everything that is visible in the image provided. Include all objects, people, and background elements. Mention the types of objects, their colors, positions, and any noticeable features or activities. If there are any brands, logos, or text, include those as well. Describe the setting, such as the type of location or event, and any other context that can be inferred. Be thorough and list as many elements as possible, even if they seem small or insignificant. Generate it as a list of elements"

    with open(os.getcwd() + "/" + image_path, "rb") as image_file:
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
        os.chdir('..')

        # Load and process the image
        image_path = os.path.join('server/images', img_name)

        # Get an in-depth summary from OpenAI
        summary = get_in_depth_summary(image_path)
        print(f"\nIn-Depth Summary:\n{summary}")
        return summary

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

def checkai_instr_vs_summaries(instr, img, audio):
    try:
        prompt = f"Instruction: {instr}\nImage Summary: {img}\nAudio Transcript: {audio}\nUsing the provided instruction compare it to the Image Summary and Audio Transcript and provide me a short response with what you can gather. I want to know if the user is doing the task correctly based on the instruction. If they are, provide me a Good job along with a short message of what they are doing right that matches the instruction. If they are not doing it right, provide me with a Thats not it along with a description of what doesnt match the instruction. Remember keep the responses short. In the last sentence of your response include either \"Proceed\" or \"Do Not Proceed\" based on if the person did the task or not."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"