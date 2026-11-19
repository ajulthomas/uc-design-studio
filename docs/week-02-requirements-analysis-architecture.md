# Week 2 — Requirements Analysis, System Design, Architectural Patterns & Tech Stack

## Requirements analysis, at the architecture level

Before touching code, it's worth stating the handful of requirements that actually drove this
app's shape (the deeper elicitation/sign-off process is Weeks 3–4; this is the "so what did the
system end up needing to do" summary):

- Deliver a conversational tutor, not a form or dashboard → needs a chat UI.
- The tutoring behaviour (tone, boundaries, the Mae persona, the 12 arcs) is long and nuanced →
  belongs in a prompt document, not scattered across code.
- The team is small and Python-first (LangChain, model SDKs) → backend-heavy stack, UI should be
  "free" rather than hand-built.
- The underlying LLM provider/model will almost certainly change over time (confirmed in practice
  — see the `da5ca89`/`b6b8012` commits changing the default model) → the model must be a
  **configuration value**, not something baked into the logic.

## System design fundamentals

The whole backend is one Python module, `main.py`, organised as three layers:

1. **Configuration** — `load_dotenv()`, `NVIDIA_API_KEY`, the `MODEL` constant, and the
   `ChatNVIDIA` client built once at import time.
2. **Domain content** — `load_system_prompt()` reads `prompts/prompt-v2.md` into `SYSTEM_PROMPT`.
   This is the layer that encodes *what Yurung is allowed to say*; changing the tutor's behaviour
   is a content edit, not a code change (compare `prompt-v1.md` vs `prompt-v2.md` in the repo —
   that diff *is* a requirements revision).
3. **Interaction handlers** — Chainlit's `@cl.on_chat_start` and `@cl.on_message` hooks, which are
   the only two entry points into the system.

```
Browser (Chainlit UI)
   │  on_chat_start / on_message
   ▼
main.py
   │  SystemMessage(SYSTEM_PROMPT) + session history
   ▼
ChatNVIDIA  (LangChain chat-model interface)
   │  HTTPS
   ▼
NVIDIA NIM hosted endpoint (integrate.api.nvidia.com)
```

## Architectural pattern: thin orchestration over a hosted model

This isn't a classic layered web app (no controllers/services/repositories, no database). The
pattern here is closer to **gateway/adapter**: the app's own logic is deliberately small, and
almost all the "intelligence" is delegated to (a) the system prompt content and (b) the hosted
LLM. The only state the app manages itself is the per-session message list
(`cl.user_session.get("history")`), kept in memory.

Trade-offs that come with that pattern, worth writing down as non-functional requirements later:

- **Pro**: very little backend code to maintain; model/provider swaps are a one-line change.
- **Con**: no persistence — a server restart or session timeout loses the conversation. Fine for a
  studio exercise; would need revisiting if transcripts needed to be reviewed by instructors.
- **Con**: the app is only as reliable as the upstream model. This stopped being theoretical —
  see the Week 5 notes on the `/v1/models` vs `/v1/chat/completions` entitlement issue, where the
  previously-configured model and API key stopped working entirely without any code change.

## Technology stack decisions

| Layer | Choice | Why |
|---|---|---|
| Backend language | Python 3.11+ | LangChain and every current LLM SDK are Python-first. |
| Chat UI | Chainlit | Ships streaming, a message list, a "thinking" step indicator, and (previously) a settings widget out of the box — no custom frontend needed for a single-conversation tutor. |
| LLM orchestration | LangChain core (`SystemMessage`/`HumanMessage`/`AIMessage`, `astream`) | Provider-agnostic message types; swapping `ChatNVIDIA` for another LangChain chat model later is a small, contained change. |
| Model host | NVIDIA NIM (`langchain-nvidia-ai-endpoints`) | Hosted inference, no GPU to manage; see Week 5 for the real auth/entitlement issues this introduced. |
| Deployment | Procfile-based (`web: chainlit run main.py ...`) | Matches a simple PaaS deploy model (one web process, port from `$PORT`). |

**On "React frontend where required":** this project currently has **no** separate frontend, and
deliberately so — Chainlit's built-in chat UI already covers every interaction this app needs
(streaming messages, a status step, previously a model-select widget). A bespoke React frontend
would only be justified if the studio needed UI Chainlit can't provide — e.g. a custom arc browser,
a student dashboard, or anything outside a single chat thread. That hasn't been requested, so the
"React where required" clause currently resolves to "not required."
