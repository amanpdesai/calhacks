import os
import openai
from dotenv import load_dotenv
import asyncio
from uagents import Agent, Context, Model
from utils.message_config import system_prompt, user_prompt, catheter_instruction

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ContextPrompt(Model):
    context: str
    text: str


class Response(Model):
    text: str


agent = Agent(
    name="user",
    endpoint="http://localhost:8000/submit",
)

print("uAgent created successfully: ", agent.address)

AI_AGENT_ADDRESS = agent.address

prompt = ContextPrompt(
    context=system_prompt+user_prompt,
    text=catheter_instruction,
)

# Function to make synchronous OpenAI API call in an asynchronous context
async def get_openai_response(prompt_context, prompt_text):
    try:
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",  # Replace with "gpt-4" if you have access
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that finds and fixes bugs in code.",
                },
                {"role": "user", "content": f"{prompt_context}\n\n{prompt_text}"},
            ],
            max_tokens=150,
            temperature=0.5,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return None


# Send message and make request to OpenAI API
@agent.on_event("startup")
async def send_message(ctx: Context):
    try:
        print("Sending request to OpenAI...")
        # Get response from OpenAI asynchronously
        text_response = await get_openai_response(prompt.context, prompt.text)

        if text_response:
            # Manually trigger handle_response function with the OpenAI response
            await handle_response(ctx, AI_AGENT_ADDRESS, Response(text=text_response))
            print("Request sent and response received from OpenAI.")
        else:
            print("Failed to get a response from OpenAI.")
    except Exception as e:
        print(f"Error occurred while making request to OpenAI: {e}")


# Handle OpenAI API response
@agent.on_message(Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    try:
        print("Receiving response from OpenAI...")
        ctx.logger.info(f"Received response from {sender}: {msg.text}")
    except Exception as e:
        print(f"Error occurred while handling response: {e}")


if __name__ == "__main__":
    agent.run()