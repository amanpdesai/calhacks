from uagents import Agent, Context
from models.models import ContextPrompt, Response
from uagents.setup import fund_agent_if_low
from utils.openai_api import get_openai_response
import pymysql
import logging
from utils.text_to_speech import text_to_wav
import re

logger = logging.getLogger("assistant_agent")

assistant_agent = Agent(
    name="assistant_agent",
    seed="assistant_seed_unique",
    port=8001,
    endpoint="http://localhost:8001/submit",
)

# Connect to the SingleStore database
connection = pymysql.connect(
    host="svc-f90325a9-8b27-495d-a436-7cb5c7764c62-dml.aws-oregon-3.svc.singlestore.com",
    user="admin",
    password="Flj3M3k6N1of0CXLuR73YiPRMkf9JiTj",
    database="instructions",
    port=3306,
)

fund_agent_if_low(assistant_agent.wallet.address())


def query_database_validation(step):
    """
    Function to query the database for validation of the current step.
    Returns a list of tuples containing (step_number, Speaker, Judgement).
    """
    try:
        with connection.cursor() as cursor:
            sql_query = f"SELECT * FROM Step_{step} AS s WHERE s.Speaker = 'Judgement'"
            cursor.execute(sql_query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        logger.error(f"Database query failed for Step_{step}: {e}")
        return []

# print(query_database_validation("Step_1"))


def parse_instructions(instruction_text):
    """
    Function to parse the catheter_instruction and turn it into a list.
    Each element in the list is a non-empty line from the instructions.
    """
    try:
        if instruction_text is None:
            raise ValueError("instruction_text cannot be None")

        # Split the instruction_text into lines and strip whitespace
        lines = instruction_text.strip().split("\n")
        instruction_list = [line.strip() for line in lines if line.strip()]

        return instruction_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def increment_step(ctx):
    """
    Function to move to the next step and update the current step in the context storage.
    """
    current_step = ctx.storage.get("current_step")
    current_step += 1
    ctx.storage.set("current_step", current_step)
    return current_step

def format_step_name(step):
    """
    Converts a step string from 'Step X' to 'Step_X' using regular expressions.

    Parameters:
        step_string (str): The original step string (e.g., 'Step 1').

    Returns:
        str: The formatted step string (e.g., 'Step_1').
    """
    step = str(step)
    print(step)
    formatted_string = "Step_" + step
    print(formatted_string)
    return formatted_string


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
            print("test")
            catheter_instruction = (
                msg.text
            )  # Assuming msg.text contains the instructions
            print("test2")
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
            await ctx.send(
                "agent1qwusk4z83wtga2wl9l4r8kls5j2hmvz8uyzfvz6xkuldz383mfvrwenc98k",
                Response(text=assistant_response),
            )
            text_to_wav(assistant_response, "./temp_storage/")
            logger.info(f"Sent initial step to user: Step {current_step}")
        else:
            print("instructions done")
            # Instructions are already parsed; handle user message
            current_step = ctx.storage.get("current_step")
            instruction_list = ctx.storage.get("instruction_list")
            # Log the current step
            logger.info(f"Current step: {current_step}")
            # Confirm and print the user's message
            logger.info(f"Received message from user: {msg.text}")
            table_name = format_step_name(current_step)
            # Perform database validation
            validation_results = query_database_validation(table_name)
            logger.info(f"Validation Results: {validation_results}")

            # Check if any of the judgments say 'Do Not Proceed.'
            do_not_proceed = False
            incorrect_description = ""
            for record in validation_results:
                step_number, speaker, judgement = record
                test = judgement.lower().split(".")[1]
                print(test)
                if "do not proceed" in test:
                    do_not_proceed = True
                    incorrect_description = judgement
                    break  # one 'Do Not Proceed.' is enough

            if do_not_proceed:
                step_instruction = instruction_list[current_step]

                # Craft a prompt to guide the user
                prompt_text = (
                    f"The user is making a mistake in the current step.\n\n"
                    f"Here is the instruction for Step {current_step}: {step_instruction}\n"
                    f"Here is what they are actually doing: {incorrect_description}\n\n"
                    f"Please guide them to correct their action based on the instruction."
                )

                # Get the assistant's corrective response
                corrective_response = await get_openai_response(
                    prompt_context=ctx.storage.get("context", ""),
                    prompt_text=prompt_text,
                )

                # Check if OpenAI returned a valid response
                if not corrective_response:
                    corrective_response = "I'm unable to assist with this step at the moment. Please try again later."

                # Send the corrective response to the user
                await ctx.send(sender, Response(text=corrective_response))

                # Convert text to speech and save
                text_to_wav(corrective_response, "./temp_storage/")

                logger.info(f"Provided corrective guidance for Step {current_step}")

            # Prepare the prompt
            step_instruction = instruction_list[current_step]
            user_input = msg.text
            prompt_text = (
                f"You are currently assisting a first responder by guiding them through a catheter thoracostomy. "
                f"If the user's message indicates they are finished and ready for the next step, reply with specifically and exactly the single word 'DONE' and nothing else."
                f"Of the steps you previously saw, you are currently on this step: {step_instruction}. "
                f"The user just said the following: {user_input}. "
                f"Please respond accordingly so that they can complete this step and move on. "
                f"If their message does not indicate completion or readiness to proceed, provide further instructions or guidance for the current step."
            )
            # Get the assistant's response
            assistant_response = await get_openai_response(
                prompt_context="",  # ctx.storage.get("context"),
                prompt_text=prompt_text,
            )

            print("assistant response", assistant_response.strip().lower())
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
                    text_to_wav(
                        "The procedure is complete. If you have any questions, feel free to ask.",
                        "./temp_storage/",
                    )
                    ctx.storage.set("procedure_complete", True)
                    logger.info("Procedure completed.")
                else:
                    # Send the next step without the 'done' feature
                    step_instruction = instruction_list[current_step]
                    print("current step without done feature: ", current_step)
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
                    text_to_wav(assistant_response, "./temp_storage/")
                    logger.info(f"Moved to next step: Step {current_step}")
            else:
                # Send the assistant's response to the user
                # await ctx.send(sender, Response(text=assistant_response))
                text_to_wav(assistant_response, "./temp_storage/")
                logger.info(f"Sent guidance to user on Step {current_step}")
    except Exception as e:
        logger.error(f"Error in assistant agent: {e}")
        await ctx.send(
            sender,
            Response(
                text="An error occurred while processing your request. Please try again later."
            ),
        )
