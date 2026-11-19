# Week 6 — HCI Design Principles, User Research, Personas & Journey Mapping

## Two layers of HCI in this project

This project is unusual in that it contains **two** separate HCI problems stacked on top of each
other: the HCI of the chat app itself (for students), and a persona/journey-mapping exercise that
is the *subject matter the app teaches* (Mae, and the 12 arcs). Worth treating both.

## Layer 1 — HCI of the app, for its real users (design students)

Concrete principles already reflected in `main.py` and the prompt:

- **Visibility of system status** — the `cl.Step(name="Thinking", ...)` indicator and token-by-
  token streaming mean a student is never looking at a blank screen wondering if anything is
  happening.
- **Set expectations immediately** — the `on_chat_start` welcome message tells the student who
  Yurung is and what to do first ("Tell me about the design challenge you are currently
  exploring"), rather than dropping them into an empty chat box.
- **Constrain the interaction deliberately** — the system prompt's "ask one question at a time"
  and "do not provide design solutions" rules are an HCI decision as much as a pedagogical one:
  a tutor that dumps a wall of answers would be easier to build, but worse at the actual job.
  Removing the model-picker settings panel (Week 4) is the same principle applied to the UI layer
  — fewer controls, less for a student to misconfigure.
- **Graceful failure** — when a model call fails, the student sees a plain-language apology
  message instead of a broken UI or a silent hang. Error states are part of the interface, not an
  afterthought.

## Layer 2 — the persona and journey map already built into the product

The system prompt (`prompts/prompt-v2.md`) is, functionally, a fully worked persona and journey
map that students are asked to design *for*:

**Persona: Mae** — a respected Aboriginal Elder on Ngunnawal Country near Canberra; 40+ years in
the same home; changing mobility (stairs becoming difficult); refuses to leave because Country,
memory, and responsibility are tied to the place; still an active community resource (keeps native
plants, answers questions from young people); wary of government "help" becoming control; will
accept support only if it respects her authority over her own life. This is a genuinely strong
example persona for teaching purposes — it has a concrete biography, explicit values, and named
tensions, not just demographics.

**Journey mapping, via the 12 story arcs** — each arc is structured identically: a micro-story
(a specific, situated moment), a cultural anchor (the underlying value at stake), a key tension
(the actual design conflict), and reflection prompts (questions, not answers). That four-part
structure *is* a journey-map template, reusable for any arc:

```
Arc N
 ├─ Micro-story        → a concrete scene the persona experiences
 ├─ Cultural anchor     → the value the scene is grounded in
 ├─ Key tension          → what's actually in conflict
 └─ Reflection prompts   → what the student should interrogate
```

Students effectively do their own user research by reading the arcs and asking Yurung reflective
questions — the app's whole pedagogical model is "practice HCI/user-research thinking on a
well-constructed example before doing it on a real project."

## A persona and journey map for the app's own real user

Turning the method back on the product itself:

**Persona: a design studio student** — enrolled in a University of Canberra design course;
comfortable with a chat interface but not an AI expert; under time pressure across a semester;
motivated but can default to wanting a quick answer if the tool lets them.

**Journey:**

1. **Entry** — opens the app, reads the welcome message, understands this is a guide, not an
   answer engine.
2. **Exploration** — names a design challenge or arc; receives a reflective question instead of a
   solution; may feel mild friction here (expecting an answer, getting a question back).
3. **Research loop** — goes to read suggested material (e.g. public cultural resources named per
   arc), then returns to continue the conversation with more context.
4. **Breakdown case** — the model fails to respond (provider outage, retired model). The student
   sees a clear error instead of a crash, and can simply resend — the journey has a designed
   recovery path rather than a dead end.
5. **Exit** — session ends; nothing is saved. If the course later requires revisiting a past
   conversation, this is the point where the current design falls short (ties back to Week 5's
   data-persistence note).
