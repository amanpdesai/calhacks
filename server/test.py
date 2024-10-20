import openai
import base64

# Set your OpenAI API key
openai.api_key = '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'

client = openai.OpenAI(
    api_key=openai.api_key
)

# Define the image file path and the prompt
image_path = '/Users/amanp/Desktop/code/Calhacks/server/images/pfp.png'
prompt = "Describe in detail everything that is visible in the image provided. Include all objects, people, and background elements. Mention the types of objects, their colors, positions, and any noticeable features or activities. If there are any brands, logos, or text, include those as well. Describe the setting, such as the type of location or event, and any other context that can be inferred. Be thorough and list as many elements as possible, even if they seem small or insignificant."

img_type = "image/png"


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
print("Generated Description:\n", summary)
