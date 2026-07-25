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

# Default model used when the list cannot be fetched or the user's
# selection is no longer available.
DEFAULT_MODEL = "openai/gpt-oss-20b" # meta/llama-3.3-70b-instruct" # "minimaxai/minimax-m3"

# Shared kwargs for the ChatNVIDIA client so every model instance is
# constructed consistently.
LLM_KWARGS = {
    "api_key": NVIDIA_API_KEY,
    "temperature": 1,
    "top_p": 1,
    "max_completion_tokens": 4096,
}

# Shared default settings widget id so we can refresh it later.
MODEL_SELECT_ID = "model"


async def get_available_model_ids() -> list[str]:
    """Return the list of model ids available via the NVIDIA endpoint.

    Falls back to a single default id if the request fails so the app
    keeps working even if the catalog endpoint is unreachable.
    """
    try:
        models = await cl.make_async(ChatNVIDIA.get_available_models)(
            api_key=NVIDIA_API_KEY
        )
        ids = [m.id for m in models]
        # Keep the default reachable in the dropdown even if the catalog
        # does not explicitly list it.
        if DEFAULT_MODEL not in ids:
            ids.insert(0, DEFAULT_MODEL)
        return ids
    except Exception as e:
        # Fall back gracefully — the dropdown will only show the default.
        print(f"[model-select] Could not list models: {e}")
        return [DEFAULT_MODEL]


def make_llm(model_id: str) -> ChatNVIDIA:
    """Construct a ChatNVIDIA client for the given model id."""
    return ChatNVIDIA(model=model_id, **LLM_KWARGS)


SYSTEM_PROMPT = load_system_prompt()


async def build_settings() -> cl.ChatSettings:
    """Build the chat-settings widget with the current model list."""
    model_ids = await get_available_model_ids()
    current = cl.user_session.get("model") or DEFAULT_MODEL

    # Make sure the currently selected model is always a valid option,
    # even if it disappeared from the catalog since selection.
    if current not in model_ids:
        model_ids.insert(0, current)

    settings = cl.ChatSettings()
    settings.inputs = [
        cl.input_widget.Select(
            id=MODEL_SELECT_ID,
            label="Model",
            values=model_ids,
            initial_value=current,
            description="The language model that powers Yurung. Changes apply from the next message.",
        )
    ]
    return settings


@cl.on_chat_start
async def start():

    cl.user_session.set("history", [])

    # Set the initial model and expose the settings widget.
    cl.user_session.set("model", DEFAULT_MODEL)
    cl.user_session.set("llm", make_llm(DEFAULT_MODEL))

    await cl.Message(
        content="""
                Welcome.

                I am Yurung, your AI design tutor.

                Tell me about the design challenge
                you are currently exploring.
                """
    ).send()

    settings = await build_settings()
    await settings.send()


@cl.on_settings_update
async def on_settings_update(settings: dict[str, any]):
    """Apply model changes from the settings widget without restarting."""
    model_id = settings.get(MODEL_SELECT_ID)
    if not model_id:
        return

    available = await get_available_model_ids()

    # Graceful fallback if the selected model disappeared while the drop
    # down was open or the catalog changed under us.
    if model_id not in available:
        await cl.Message(
            content=(
                f"The model "**{model_id}**" is no longer available. "
                f"Reverting to "**{DEFAULT_MODEL}**"."
            ),
            author="system",
        ).send()
        model_id = DEFAULT_MODEL
        # Reflect the fallback back into the widget.
        cl.user_session.set("model", model_id)
        await (await build_settings()).refresh()
        return

    cl.user_session.set("model", model_id)
    cl.user_session.set("llm", make_llm(model_id))


@cl.on_message
async def main(message: cl.Message):

    # Immediately show a "Thinking..." status so the user sees feedback
    # while the model is warming up and before the first token arrives.
    model_id = cl.user_session.get("model") or DEFAULT_MODEL
    llm = cl.user_session.get("llm") or make_llm(model_id)

    async with cl.Step(name="Thinking", type="llm") as step:
        step.output = "Thinking…"
        await step.update()

        history = cl.user_session.get("history")
        history.append(HumanMessage(content=message.content))
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + history

        # Create the streaming message up front so it can receive tokens
        # the instant the first one arrives from the model. Tag it with
        # the active model so the choice is visible per response.
        msg = cl.Message(content="", tags=[model_id])
        full_response = ""
        first_token_seen = False

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

        await msg.send()

        history.append(AIMessage(content=full_response))
        cl.user_session.set("history", history)