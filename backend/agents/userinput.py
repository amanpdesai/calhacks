from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from models.models import ContextPrompt, Response
from utils.message_config import system_prompt, user_prompt, catheter_instruction
import logging

# Initialize the User Agent
user_agent = Agent(
    name="user_agent",
    seed="user_seed",  # need a unique seed
    port=8002,
    endpoint="http://localhost:8002/submit",
)

logger = logging.getLogger("user_agent")

fund_agent_if_low(user_agent.wallet.address())


@user_agent.on_event("startup")
async def start_conversation(ctx: Context):
    try:
        ctx.logger.info(user_agent.address)
        logger.info("User is starting the conversation...")

        initial_context = system_prompt + user_prompt
        initial_text = catheter_instruction

        # Initial message to the assistant agent
        prompt = ContextPrompt(
            context=initial_context,
            text=initial_text,
        )
        await ctx.send(
            "agent1q2h2l2gry8ak32am7x7un5c08kuzggv9szxxpqxwn6ku4lkvtud57lk6c3d", prompt
        )  # Assistant's endpoint
        logger.info("User sent initial message to assistant.")
    except Exception as e:
        logger.error(f"Error in user agent during startup: {e}")


@user_agent.on_message(Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    try:
        logger.info(f"User received response from assistant:\n{msg.text}\n")
        print(f"Assistant Response: {msg.text}\n")

        # Ask for user input
        user_input = input("Enter your response: ")

        # Send the user input as the next message to the assistant
        prompt = ContextPrompt(
            context="",  # No additional context needed for now
            text=user_input,
        )
        await ctx.send(sender, prompt)
        logger.info(f"User sent response to assistant: {user_input}")
    except Exception as e:
        logger.error(f"Error in user agent while handling response: {e}")
