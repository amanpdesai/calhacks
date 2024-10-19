from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from models.models import ContextPrompt, Response
from utils.message_config import system_prompt, user_prompt, catheter_instruction
from utils.config import setup_logging

# Initialize the User Agent
user_agent = Agent(
    name="user_agent",
    seed="user_seed",  # need a unique seed
    port=8002,
    endpoint="http://localhost:8002/submit",
)

logger = setup_logging()

fund_agent_if_low(user_agent.wallet.address())


@user_agent.on_event("startup")
async def start_conversation(ctx: Context):
    try:
        ctx.logger.info(user_agent.address)
        logger.info("User is starting the conversation...")

        initial_context = system_prompt + user_prompt
        initial_text = catheter_instruction

        # initial message to the assistant agent
        prompt = ContextPrompt(
            context=initial_context,
            text=initial_text,
        )
        await ctx.send(
            "agent1qfzll7xq6t8d9rx5n3cnql32me650q2sakexpc979u0luhn702jh2af5mds", prompt
        )  # assistant's endpoint
        logger.info("User sent initial message to assistant.")
    except Exception as e:
        logger.error(f"Error in user agent during startup: {e}")


@user_agent.on_message(Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    try:
        logger.info(f"User received response from assistant:\n{msg.text}\n")
        # Simulate user confirmation for each step
        if "procedure is complete" in msg.text.lower():
            logger.info("Procedure completed.")
            return

        user_confirmation = "Yes, proceed to the next step."
        # Send confirmation back to assistant
        prompt = ContextPrompt(
            context="",  # No additional context needed
            text=user_confirmation,
        )
        await ctx.send(sender, prompt)
        logger.info("User sent confirmation to assistant.")
    except Exception as e:
        logger.error(f"Error in user agent while handling response: {e}")
