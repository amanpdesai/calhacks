from uagents import Agent, Context
from models.models import ImagePrompt, ImageResponse
from uagents.setup import fund_agent_if_low
from utils.openai_api import get_openai_response
from utils.config import setup_logging
import base64
import io
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

logger = setup_logging()

# Initialize the agent
image_agent = Agent(
    name="image_agent",
    seed="image_agent_seed_unique",
    port=8002,
    endpoint="http://localhost:8002/submit",
)

# Fund the agent if the balance is low
fund_agent_if_low(image_agent.wallet.address())

# Load BLIP model and processor during startup
@image_agent.on_event("startup")
async def startup_event(ctx: Context):
    try:
        logger.info(f"Image Agent Address: {image_agent.address}")
        # Load BLIP model and processor
        ctx.storage.set(
            "processor",
            BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
        )
        ctx.storage.set(
            "model",
            BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
        )
        logger.info("BLIP model and processor loaded successfully.")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

# Handle incoming messages with image data
@image_agent.on_message(ImagePrompt)
async def handle_image_message(ctx: Context, sender: str, msg: ImagePrompt):
    try:
        # Decode the base64-encoded image data
        image_data = base64.b64decode(msg.image_data)
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # Retrieve the BLIP model and processor from storage
        processor = ctx.storage.get("processor")
        model = ctx.storage.get("model")

        # Generate caption using BLIP
        inputs = processor(image, return_tensors='pt')
        with torch.no_grad():
            out = model.generate(**inputs, max_length=50)
            caption = processor.decode(out[0], skip_special_tokens=True)
            logger.info(f"Generated Caption: {caption}")

        # Prepare prompt for in-depth summary
        prompt_text = (
            f"Provide a thorough and detailed analysis, including possible contexts, emotions, and implications, "
            f"based on the following image description:\n\n'{caption}'"
        )

        # Get in-depth summary from OpenAI
        in_depth_summary = await get_openai_response(
            prompt_context="",
            prompt_text=prompt_text,
            max_tokens=500,
            temperature=0.7
        )

        # Send the response back to the user
        await ctx.send(sender, ImageResponse(
            caption=caption,
            summary=in_depth_summary
        ))
        logger.info("In-depth summary sent to the user.")
    except Exception as e:
        logger.error(f"Error in image agent: {e}")
        await ctx.send(sender, ImageResponse(
            caption="",
            summary="An error occurred while processing your image. Please try again later."
        ))

# Run the agent
if __name__ == "__main__":
    image_agent.run()
