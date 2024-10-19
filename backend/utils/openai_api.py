import openai
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


async def get_openai_response(prompt_context, prompt_text):
    try:
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_context},
                {"role": "user", "content": prompt_text},
            ],
            max_tokens=1500,
            temperature=0.5,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return None
