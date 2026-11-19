import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import chainlit as cl

from langchain_nvidia_ai_endpoints import ChatNVIDIA


def load_system_prompt() -> str:
    prompt_path = Path("prompts/prompt-v2.md")

    return prompt_path.read_text(encoding="utf-8")


# Load environment variables from .env
load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

MODEL = "meta/muse-glimmer-30b"

SYSTEM_PROMPT = load_system_prompt()

llm = ChatNVIDIA(
    model=MODEL,
    api_key=NVIDIA_API_KEY,
    temperature=1,
    top_p=1,
    max_completion_tokens=4096,
)


@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])

    await cl.Message(
        content="""
                Welcome.

                I am Yurung, your AI design tutor.

                Tell me about the design challenge
                you are currently exploring.
                """
    ).send()


@cl.on_message
async def main(message: cl.Message):

    async with cl.Step(name="Thinking", type="llm") as step:
        step.output = "Thinking…"
        await step.update()

        history = cl.user_session.get("history")
        history.append(HumanMessage(content=message.content))
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + history

        # Create the streaming message up front so it can receive tokens
        # the instant the first one arrives from the model.
        msg = cl.Message(content="")
        full_response = ""
        first_token_seen = False

        try:
            async for chunk in llm.astream(messages):
                token = chunk.content
                if not token:
                    continue

                full_response += token
                await msg.stream_token(token)

                # Once the first chunk is in flight, clear the thinking
                # placeholder so the streamed answer takes over the view.
                if not first_token_seen:
                    first_token_seen = True
                    step.output = ""
                    await step.update()
        except Exception as e:
            # The model call failed (e.g. the endpoint rejected the
            # request). Surface this clearly instead of letting an
            # unhandled exception kill the chat, and drop the unanswered
            # turn from history so it doesn't poison future requests.
            step.output = ""
            await step.update()
            history.pop()
            await cl.Message(
                content=f"Sorry, the model failed to respond ({type(e).__name__}: {e}).",
                author="system",
            ).send()
            return

        await msg.send()

        history.append(AIMessage(content=full_response))
        cl.user_session.set("history", history)
