# Week 3 — Requirement Elicitation & Stakeholder Interviews for Research Software

## Why this project counts as "research software"

chainlit-design-studio isn't a generic chatbot — it's a teaching instrument embedded in a
university design studio, built around culturally sensitive material (publicly available
Ngunnawal knowledge, used for education under explicit boundaries). That puts it in the same
category as other research/education software: the "requirements" aren't just features, they're
also ethical constraints that have to be elicited from people who aren't necessarily in the room
when code gets written.

## Who the stakeholders actually are

| Stakeholder | Interest | Where their requirements show up in the code |
|---|---|---|
| Studio instructors (University of Canberra) | Students build critical thinking, not copy-paste answers | The system prompt's rule that Yurung "does not provide design solutions" and "asks one question at a time" |
| Students (end users) | A low-friction way to explore the arcs and persona | Chainlit chat UI, streaming responses, a short welcome message |
| The Ngunnawal community (indirect stakeholder, not directly interviewed) | Cultural material is represented respectfully and only from material already made public | Explicit boundary in the prompt: "You are not an expert on Ngunnawal culture... holds firm boundaries around what is not yours — or theirs — to access" |
| Platform maintainer/developer | The app keeps running as providers/models change | Model is a swappable configuration value (Week 2); error handling around failed model calls (Week 4/5) |

The Ngunnawal-community row is the one easy to skip in a normal software project and impossible to
skip in a research-software one: nobody on the engineering side can "sign off" on cultural
accuracy on the community's behalf, so the requirement had to be elicited as a hard boundary rather
than a feature request — the tutor must *decline* to go beyond public material rather than
improvise.

## How requirements were actually elicited here

There's no recorded interview transcript in this repo, but the *elicitation artifact* is visible:
the system prompt itself. Compare `prompts/prompt-v1.md` and `prompts/prompt-v2.md` — the
differences between those two files are a real, inspectable requirements-revision record:

- Persona details for Mae (age-related mobility change, her relationship to Country, her distrust
  of government "help") read like they came directly from a subject-matter expert or existing
  case material, not from an engineer guessing.
- The "12 story arcs," each with a micro-story, a cultural anchor, a key tension, and reflection
  prompts, is a structured elicitation output — someone decided the curriculum needed to be
  broken into exactly these units, with this much supporting detail per unit, before a single
  line of `main.py` was written.

**Technique in use:** this is **document-driven elicitation** — domain experts (studio
instructors, cultural advisors) produce the authoritative content, and the engineering task is to
faithfully carry it into the system (load it verbatim as the system prompt) rather than
re-interpret it. That's a different posture than a typical feature-interview process, and worth
recognising: for this project, *editing the prompt document is doing requirements work*, even
though it looks like editing a markdown file.

## What to ask in a follow-up stakeholder interview (if doing this for real)

Questions that the current code can't answer on its own, and would need a real interview to
settle:

- Should conversations be retrievable later for instructor review, or is in-memory-only
  (current behaviour) a deliberate privacy choice?
- Is there a maximum/expected class size (session volume) the app needs to support concurrently?
- Who is authorised to approve changes to the Mae persona or the arcs — is there a review step
  before a `prompt-v3.md` would go live?
