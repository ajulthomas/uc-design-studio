# Week 5 — Data Modelling & API/Interface Design Between System Components

## The actual data model

There is no database in this app — the entire "data model" is the shape of objects passed between
components in memory, for the lifetime of one chat session:

```python
history: list[HumanMessage | AIMessage]       # cl.user_session.get("history")
messages = [SystemMessage(SYSTEM_PROMPT)] + history   # what actually gets sent to the model
```

- `SystemMessage` — one, constant, built once from `prompts/prompt-v2.md` at import time.
- `HumanMessage` / `AIMessage` — one pair appended per turn; this *is* the conversation record.
- Nothing is persisted. When the Chainlit session ends, the history is gone. That's a data-
  modelling decision worth stating explicitly (see Week 4's NFRs) rather than an accident — if a
  future requirement needs instructors to review transcripts, this is the first thing that has to
  change, and it would mean introducing an actual store (file, database) keyed by session/user.

## Interfaces between components

**1. Chainlit ↔ application code** — event-hook interface, not a network call:

| Hook | Trigger | What it owns |
|---|---|---|
| `@cl.on_chat_start` | New session | Resets `history` to `[]`, sends the welcome message |
| `@cl.on_message` | Each user message | Appends to history, streams a response, handles failure |

Session-scoped state passes through `cl.user_session` as a simple key/value store (`"history"` is
the only key currently used).

**2. Application ↔ LLM client** — the LangChain chat-model contract:

```python
llm = ChatNVIDIA(model=MODEL, api_key=NVIDIA_API_KEY, temperature=1, top_p=1,
                  max_completion_tokens=4096)

async for chunk in llm.astream(messages):   # messages: list of LangChain Message objects
    token = chunk.content                   # str
```

This interface is provider-agnostic by design — `ChatNVIDIA` could be swapped for any other
LangChain chat model implementing the same `astream`/`invoke` contract without touching
`on_message` at all. That's the payoff of the Week 2 architecture decision to route everything
through LangChain's message types instead of a provider-specific SDK shape.

**3. LLM client ↔ NVIDIA NIM REST API** — the actual HTTP boundary, and where a real integration
issue surfaced this project:

| Endpoint | Purpose | Auth behaviour observed |
|---|---|---|
| `GET /v1/models` | List available models | Worked with a "Personal Key" lacking the right entitlement |
| `POST /v1/chat/completions` | Run inference | Returned `401 Invalid JWT serialization` with that same key |

The lesson for interface design: **a successful call to one endpoint of a third-party API does
not prove the credential works for another endpoint.** `GET /v1/models` only proves the key is
*valid*, not that it's *entitled* for inference. The actual fix was generating a new NVIDIA
Personal Key with "Public API Endpoints" explicitly checked under "Services Included" — a
permissions/entitlement issue entirely on the provider side, invisible from this app's code. Any
future provider integration should be smoke-tested against the *specific* endpoint it depends on,
not just a lightweight "is the key valid" check.

**4. Application ↔ deployment platform** — the `Procfile` contract:

```
web: chainlit run main.py --host 0.0.0.0 --port $PORT
```

This is itself a (very small) interface: the platform promises a `$PORT` env var and routes
traffic to it; the app promises to bind `0.0.0.0:$PORT` and speak HTTP. Two early commits
("resolves build error due to multiple package managers", "resolves runtime error due to incorrect
procfile") were both failures at exactly this boundary — a reminder that deployment contracts are
interfaces too, and worth testing like one.
