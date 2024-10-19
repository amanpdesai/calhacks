from uagents import Agent, Context
from models.models import ContextPrompt, Response
from uagents.setup import fund_agent_if_low
from utils.openai_api import get_openai_response
from utils.config import setup_logging
import re


assistant_agent = Agent(
    name="assistant_agent",
    seed="assistant_seed",  # need a unique seed
    port=8001,
    endpoint="http://localhost:8001/submit",
)

logger = setup_logging()

fund_agent_if_low(assistant_agent.wallet.address())


@assistant_agent.on_event("startup")
async def start_conversation(ctx: Context):
    try:
        ctx.logger.info(assistant_agent.address)
    except Exception as e:
        logger.error(f"Error in user agent during startup: {e}")


@assistant_agent.on_message(ContextPrompt)
async def handle_user_message(ctx: Context, sender: str, msg: ContextPrompt):
    try:
        if not ctx.storage.get("procedure_complete"):
            # Initialize the procedure conversation
            logger.info(
                f"Received message from {sender}: {msg.text[:50]}..."
            )  # Log first 50 chars

            # Extract steps using regex
            # This regex matches "Step {number}: {instruction}" across multiple lines
            step_pattern = re.compile(
                r"Step\s+(\d+):\s+(.*?)(?=Step\s+\d+:|$)", re.DOTALL
            )
            matches = step_pattern.findall(msg.text)

            if not matches:
                logger.error("No steps found in the provided instructions.")
                response_text = "Unable to parse the procedure steps. Please ensure the instructions are correctly formatted."
                await ctx.send(sender, Response(text=response_text))
                return

            # Sort steps based on step number to ensure correct order
            steps = sorted(matches, key=lambda x: int(x[0]))
            ctx.storage.set("steps", steps)
            ctx.storage.set("total_steps", len(steps))
            ctx.storage.set("current_step", 1)
            ctx.storage.set("procedure_complete", False)
            ctx.storage.set("instructions", msg.text)
            ctx.storage.set("context", msg.context)

            logger.info(f"Total steps found: {len(steps)}")

            # Prepare the first step
            step_number, step_instruction = steps[0]
            step_number = int(step_number)

            # Call OpenAI API to get a detailed explanation
            detailed_explanation = await get_openai_response(
                prompt_context=ctx.storage.get("context"),
                prompt_text=(
                    f"Please provide a detailed, step-by-step explanation for the following procedure step:\n\n"
                    f"Step {step_number}: {step_instruction}"
                ),
            )

            if not detailed_explanation:
                detailed_explanation = (
                    "Unable to provide a detailed explanation at this time."
                )

            response_text = (
                f"**Step {step_number}:** {step_instruction}\n\n"
                f"{detailed_explanation}\n\n"
                "Are you ready to proceed to the next step?"
            )

            # Send the detailed step to the user agent
            await ctx.send(sender, Response(text=response_text))
            logger.info(f"Sent Step {step_number} to user.")
        else:
            # User has confirmed to proceed to the next step
            logger.info(f"Proceeding to the next step for {sender}.")

            current_step = ctx.storage.get("current_step") + 1
            total_steps = ctx.storage.get("total_steps")

            if current_step > total_steps:
                response_text = "The procedure is complete. If you have any questions, feel free to ask."
                ctx.storage.set("procedure_complete", True)
                logger.info("Procedure completed.")
            else:
                # Retrieve the next step
                steps = ctx.storage.get("steps")
                step_number, step_instruction = steps[current_step - 1]
                step_number = int(step_number)
                ctx.storage.set("current_step", current_step)

                # Call OpenAI API to get a detailed explanation
                detailed_explanation = await get_openai_response(
                    prompt_context=ctx.storage.get("context"),
                    prompt_text=(
                        f"Please provide a detailed, step-by-step explanation for the following procedure step:\n\n"
                        f"Step {step_number}: {step_instruction}"
                    ),
                )

                if not detailed_explanation:
                    detailed_explanation = (
                        "Unable to provide a detailed explanation at this time."
                    )

                response_text = (
                    f"**Step {step_number}:** {step_instruction}\n\n"
                    f"{detailed_explanation}\n\n"
                    "Are you ready to proceed to the next step?"
                )

                logger.info(f"Sent Step {step_number} to user.")

            # Send the response to the user agent
            await ctx.send(sender, Response(text=response_text))
    except Exception as e:
        logger.error(f"Error in assistant agent: {e}")
        await ctx.send(
            sender,
            Response(
                text="An error occurred while processing your request. Please try again later."
            ),
        )
