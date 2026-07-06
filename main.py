import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
import chainlit as cl

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA


def load_system_prompt() -> str:
    prompt_path = Path("prompts/prompt-v2.md")

    return prompt_path.read_text(encoding="utf-8")


# Load environment variables from .env
load_dotenv()

# Read NVIDIA API key
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# llm = ChatNVIDIA(
#     model="meta/llama-3.3-70b-instruct",
#     api_key=NVIDIA_API_KEY,
#     temperature=0.2,
#     top_p=0.7,
#     max_tokens=1024
# )

# llm = ChatNVIDIA(
#     model="openai/gpt-oss-120b",
#     api_key=NVIDIA_API_KEY,
#     temperature=1,
#     top_p=1,
#     max_tokens=4096,
# )

llm = ChatNVIDIA(
  model="minimaxai/minimax-m3",
  api_key=NVIDIA_API_KEY,
  temperature=1,
  top_p=0.95,
  max_completion_tokens=8192,
)

SYSTEM_PROMPT = load_system_prompt()


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

    history = cl.user_session.get("history")

    history.append(HumanMessage(content=message.content))

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + history
    response = await llm.ainvoke(messages)
    history.append(AIMessage(content=response.content))

    cl.user_session.set("history", history)

    await cl.Message(content=response.content).send()
