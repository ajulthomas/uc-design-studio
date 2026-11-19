# Week 4 — Documenting Requirements as User Stories & Use Cases; Review and Sign-off

## Functional requirements, as user stories

Written against what this app actually does today (`main.py`, Chainlit hooks, `ChatNVIDIA`):

- *As a design student*, I want to open the app and immediately see what Yurung is and what it's
  for, so that I don't have to guess how to start. → `@cl.on_chat_start`'s welcome message.
- *As a design student*, I want my message answered with a visible "thinking" indicator and the
  reply to stream in as it's generated, so that the app doesn't feel frozen on longer responses. →
  `cl.Step(name="Thinking", ...)` + `llm.astream(...)` + `msg.stream_token(token)`.
- *As a design student*, I want Yurung to respond with questions grounded in the arc/persona
  material rather than direct design answers, so that I have to do my own thinking. → enforced
  entirely by `SYSTEM_PROMPT` content, not by code.
- *As the platform maintainer*, I want the active model to be a single configuration value, so
  that I can swap providers/models without touching the conversation logic. → the `MODEL` constant
  and the one `ChatNVIDIA(...)` construction.

## Non-functional requirements

- **Resilience to upstream failure.** The app depends entirely on a third-party hosted model. This
  stopped being a hypothetical mid-project: the original default model
  (`openai/gpt-oss-20b`) hit its real end-of-life date, and separately the NVIDIA API key in use
  turned out to lack the "Public API Endpoints" entitlement needed for `/v1/chat/completions`
  (it could still list models, just not call them). Neither failure is something the app can
  prevent — but it must not crash the chat. `main.py` wraps the streaming loop in a `try/except`
  that shows a clear in-chat error and drops the unanswered turn from history, instead of raising
  an unhandled exception.
- **Perceived latency.** Token-by-token streaming (rather than waiting for a full response) is a
  usability requirement as much as a technical one — it's the difference between the app feeling
  responsive or feeling stuck.
- **Configuration over hardcoding.** Secrets (`NVIDIA_API_KEY`) and the model identifier live in
  environment/config, never in source, both for security and so Week 1's `.env` workflow holds.
- **Simplicity over configurability.** An earlier version exposed a model-selection dropdown in the
  Chainlit settings panel (`cl.ChatSettings`, `on_settings_update`). That was deliberately removed
  — for this studio's actual use case, letting students pick a model added surface area and
  failure modes (stale catalog entries, models disappearing mid-session) without a real benefit.
  Worth recording as an NFR precisely *because* it reverses an earlier decision: "the app exposes
  exactly one model, chosen by the maintainer" is now a requirement, not an omission.

## Use case: "Student explores an arc"

1. Student opens the chat; welcome message sets expectations ("tell me about the design challenge
   you're exploring").
2. Student asks a question related to one of the 12 arcs (e.g. accessibility and Mae's stairs).
3. System appends the message to session history, sends `[SystemMessage(prompt)] + history` to the
   model.
4. Model (per system-prompt rules) responds with a reflective question tied to the matching arc,
   not a solution.
5. Response streams back token-by-token; once complete it's appended to history as an `AIMessage`.
6. **Alternate flow (failure):** the model call raises an exception (auth, retirement, timeout) →
   system shows an apology message, history is left as it was before the failed turn, and the
   student can simply try again.

## Requirements review and sign-off, as it actually happens in this repo

There's no separate formal sign-off document here — the review gate *is* the Git/GitHub workflow
from Week 1: changes land on a `dev` branch and get merged to `main` via a pull request
(`Merge pull request #1/2/3 from ajulthomas/dev` in the log). For a project this size, that PR
*is* the review step — whoever approves the merge is signing off that the change meets the
requirement it was written for. The `prompt-v1.md` → `prompt-v2.md` progression (Week 3) is the
same idea applied to content rather than code: each version is a reviewable, diffable artifact.

For anything touching the Mae persona, the arcs, or cultural content specifically, sign-off should
sit with whoever holds subject-matter/cultural authority (Week 3's "indirect stakeholder") — not
with whoever merges the PR technically. That distinction is worth being explicit about: a code
reviewer approving a prompt-file diff is not the same as a cultural reviewer approving its content.
