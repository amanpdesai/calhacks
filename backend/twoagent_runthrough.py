import os
import openai
from dotenv import load_dotenv
import asyncio
from uagents import Agent, Bureau, Context, Model
from utils.message_config import catheter_instruction, user_prompt, system_prompt
import logging

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agents.log"),
    ],
)


class ContextPrompt(Model):
    context: str
    text: str


class Response(Model):
    text: str


# Assistant agent (the AI assistant)
assistant_agent = Agent(
    name="assistant_agent",
    seed="assistant_seed",  # need a unique seed
    endpoint="http://localhost:8001/submit",
)

# User agent (the first responder)
user_agent = Agent(
    name="user_agent",
    seed="user_seed",  # need a unique seed
    endpoint="http://localhost:8002/submit",
)

print(assistant_agent._endpoints)
logging.info(f"uAgent created successfully: { assistant_agent.address}")


# OpenAI API call function
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


# Assistant agent behavior
@assistant_agent.on_message(ContextPrompt)
async def handle_user_message(ctx: Context, sender: str, msg: ContextPrompt):
    try:
        if "procedure_complete" not in ctx.storage:
            # Initialize conversation
            ctx.logger.info(f"Assistant received message from {sender}")
            ctx.storage["current_step"] = 1
            ctx.storage["procedure_complete"] = False
            ctx.storage["instructions"] = msg.text
            ctx.storage["context"] = msg.context
            # Split instructions into steps
            ctx.storage["steps"] = msg.text.split("Step ")
            ctx.storage["total_steps"] = (
                len(ctx.storage["steps"]) - 1
            )  # Adjust for indexing

            # Prepare the first step
            step_instruction = ctx.storage["steps"][ctx.storage["current_step"]].strip()
            response_text = f"**Step {ctx.storage['current_step']}:** {step_instruction}\n\nAre you ready to proceed to the next step?"

            # Send the first step to the user agent
            await ctx.send(sender, Response(text=response_text))
            ctx.logger.info(
                f"Assistant sent Step {ctx.storage['current_step']} to user."
            )
        else:
            # User has confirmed to proceed
            ctx.logger.info(f"Assistant received message from {sender}")
            ctx.storage["current_step"] += 1

            # Check if all steps are completed
            if ctx.storage["current_step"] > ctx.storage["total_steps"]:
                response_text = "The procedure is complete. If you have any questions, feel free to ask."
                ctx.storage["procedure_complete"] = True
            else:
                # Prepare the next step
                step_instruction = ctx.storage["steps"][
                    ctx.storage["current_step"]
                ].strip()
                response_text = f"**Step {ctx.storage['current_step']}:** {step_instruction}\n\nAre you ready to proceed to the next step?"
            # Send the response back to the user agent
            await ctx.send(sender, Response(text=response_text))
            ctx.logger.info(
                f"Assistant sent Step {ctx.storage['current_step']} to user."
            )
    except Exception as e:
        ctx.logger.error(f"Error in assistant agent: {e}")


# User agent behavior
@user_agent.on_event("startup")
async def start_conversation(ctx: Context):
    try:
        ctx.logger.info("User is starting the conversation...")
        # Combine prompts
        initial_context = system_prompt + "\n\n" + user_prompt
        initial_text = catheter_instruction

        # Send the initial message to the assistant agent
        prompt = ContextPrompt(
            context=initial_context,
            text=initial_text,
        )
        await ctx.send(assistant_agent.address, prompt)
        ctx.logger.info("User sent initial message to assistant.")
    except Exception as e:
        ctx.logger.error(f"Error in user agent during startup: {e}")


@user_agent.on_message(Response)
async def handle_response(ctx: Context, sender: str, msg: Response):
    try:
        ctx.logger.info(f"User received response from assistant:\n{msg.text}\n")
        # Simulate user confirmation for each step
        if "procedure is complete" in msg.text.lower():
            ctx.logger.info("Procedure completed.")
            return

        user_confirmation = "Yes, proceed to the next step."
        # Send confirmation back to assistant
        prompt = ContextPrompt(
            context="",  # No additional context needed
            text=user_confirmation,
        )
        await ctx.send(sender, prompt)
        ctx.logger.info("User sent confirmation to assistant.")
    except Exception as e:
        ctx.logger.error(f"Error in user agent while handling response: {e}")


# Set up the Bureau and add agents
bureau = Bureau()
bureau.add(assistant_agent)
bureau.add(user_agent)

if __name__ == "__main__":
    bureau.run()
