from uagents import Agent, Context
from models.models import ContextPrompt, Response
from uagents.setup import fund_agent_if_low
from utils.openai_api import get_openai_response
from utils.config import setup_logging

logger = setup_logging()

assistant_agent = Agent(
    name="assistant_agent",
    seed="assistant_seed_unique",  # Ensure this seed is unique
    port=8001,
    endpoint="http://localhost:8001/submit",
)

fund_agent_if_low(assistant_agent.wallet.address())


def parse_instructions(instruction_text):
    """
    Function to parse the catheter_instruction and turn it into a list.
    Each element in the list is a line from the instructions, including empty lines.
    """
    lines = instruction_text.strip().split("\n")
    instruction_list = [line.strip() for line in lines]
    # Print the list for verification
    print("Parsed Instruction List:")
    for idx, line in enumerate(instruction_list):
        print(f"{idx}: {line}")
    return instruction_list


def increment_step(ctx):
    """
    Function to move to the next step and update the current step in the context storage.
    """
    current_step = ctx.storage.get("current_step", 0)
    current_step += 1
    ctx.storage.set("current_step", current_step)
    return current_step


@assistant_agent.on_event("startup")
async def start_conversation(ctx: Context):
    try:
        logger.info(f"Assistant Agent Address: {assistant_agent.address}")
    except Exception as e:
        logger.error(f"Error during startup: {e}")


@assistant_agent.on_message(ContextPrompt)
async def handle_user_message(ctx: Context, sender: str, msg: ContextPrompt):
    try:
        # Check if the instructions have been parsed and stored
        if not ctx.storage.get("instructions_parsed"):
            # Parse the catheter_instruction and store it
            catheter_instruction = (
                msg.text
            )  # Assuming msg.text contains the instructions
            instruction_list = parse_instructions(catheter_instruction)
            ctx.storage.set("instruction_list", instruction_list)
            ctx.storage.set("instructions_parsed", True)
            ctx.storage.set("current_step", 0)  # Start at step 0
            ctx.storage.set("procedure_complete", False)
            ctx.storage.set("context", msg.context)
            # Initialize conversation by sending the first step
            current_step = ctx.storage.get("current_step")
            step_instruction = instruction_list[current_step]
            # Prepare the initial prompt without the 'done' feature
            prompt_text = (
                f"You are currently assisting a first responder by guiding them through a catheter thoracostomy. "
                f"Of the steps you previously saw, you are currently on this step: {step_instruction}. "
                f"Please respond accordingly so that they can complete this step and move on."
            )
            # Get the assistant's response
            assistant_response = await get_openai_response(
                prompt_context=ctx.storage.get("context"),
                prompt_text=prompt_text,
            )
            # Send the response to the user
            await ctx.send(sender, Response(text=assistant_response))
            logger.info(f"Sent initial step to user: Step {current_step}")
        else:
            # Instructions are already parsed; handle user message
            current_step = ctx.storage.get("current_step", 0)
            instruction_list = ctx.storage.get("instruction_list")
            # Log the current step
            logger.info(f"Current step: {current_step}")
            # Confirm and print the user's message
            logger.info(f"Received message from user: {msg.text}")
            # Prepare the prompt
            step_instruction = instruction_list[current_step]
            user_input = msg.text
            prompt_text = (
                f"You are currently assisting a first responder by guiding them through a catheter thoracostomy. "
                f"Of the steps you previously saw, you are currently on this step: {step_instruction}. "
                f"The user just said the following: {user_input}. "
                f"Please respond accordingly so that they can complete this step and move on. "
                f"If the user provides any confirmation that they are done with the step, ONLY generate a reply to this message saying the word 'done'. "
                f"Otherwise, draft out a response to guide them through the current step."
            )
            # Get the assistant's response
            assistant_response = await get_openai_response(
                prompt_context=ctx.storage.get("context"),
                prompt_text=prompt_text,
            )
            # Check the assistant's response
            if assistant_response.strip().lower() == "done":
                # User confirmed completion; move to the next step
                current_step = increment_step(ctx)
                if current_step >= len(instruction_list):
                    # Procedure is complete
                    await ctx.send(
                        sender,
                        Response(
                            text="The procedure is complete. If you have any questions, feel free to ask."
                        ),
                    )
                    ctx.storage.set("procedure_complete", True)
                    logger.info("Procedure completed.")
                else:
                    # Send the next step without the 'done' feature
                    step_instruction = instruction_list[current_step]
                    prompt_text = (
                        f"You are currently assisting a first responder by guiding them through a catheter thoracostomy. "
                        f"Of the steps you previously saw, you are currently on this step: {step_instruction}. "
                        f"Please respond accordingly so that they can complete this step and move on."
                    )
                    assistant_response = await get_openai_response(
                        prompt_context=ctx.storage.get("context"),
                        prompt_text=prompt_text,
                    )
                    await ctx.send(sender, Response(text=assistant_response))
                    logger.info(f"Moved to next step: Step {current_step}")
            else:
                # Send the assistant's response to the user
                await ctx.send(sender, Response(text=assistant_response))
                logger.info(f"Sent guidance to user on Step {current_step}")
    except Exception as e:
        logger.error(f"Error in assistant agent: {e}")
        await ctx.send(
            sender,
            Response(
                text="An error occurred while processing your request. Please try again later."
            ),
        )
