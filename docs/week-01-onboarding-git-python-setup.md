# Week 1 — Project Onboarding, Git/GitHub, Python Environment Setup

## Project brief and scope

**chainlit-design-studio** is the codebase behind **Yurung**, an AI design tutor used in a design
studio at the University of Canberra. Students on the studio work on projects involving the
Ngunnawal community, and Yurung's job is to guide their thinking — not to design for them.

Concretely, the "product" is one Python process (`main.py`) that:

- Serves a chat UI via **Chainlit** (no separate frontend to build or host).
- Loads a system prompt from `prompts/prompt-v2.md` that encodes the tutor's identity, tone, and
  a structured curriculum (a fictional persona, **Mae**, and 12 "story arcs" students explore).
- Streams responses from a hosted LLM reached through **LangChain**'s `ChatNVIDIA` client.

Scope boundary worth noting from day one: Yurung is explicitly *not* a subject-matter expert on
Ngunnawal culture, and does not provide design answers. That constraint is a product requirement,
not just a tone preference — it shows up again in Week 4 (requirements) and Week 6 (HCI).

Out of scope for this codebase (at least currently): no database, no user accounts, no persisted
chat history across restarts, no custom frontend. Session state lives only in memory for the
duration of a Chainlit session (`cl.user_session`).

## Git and GitHub fundamentals, applied to this repo

The repo's own history is a reasonable case study. Reading `git log --oneline` top to bottom
(oldest first) tells a real story:

```
c5895e3 initial release
4b17af3 configures for deployment
d8ab2f6 resolves build error due to multiple package managers
96cf618 resolves build error due to multiple package managers
7cac0b3 resolves runtime error due to incorrect procfile
0304dba tests minimax m3
8f841c7 implements streaming
0e744f0 shows thinking status
635c7b3 Merge pull request #1 from ajulthomas/dev
6eacc73 adds options to changes the model
69d484f Merge pull request #2 from ajulthomas/dev
b6b8012 chnages teh default model to Meta/Llama 3 70B
8c2523b Merge pull request #3 from ajulthomas/dev
da5ca89 updates the default model to gpt-oss-20b
```

Two things to take from this:

1. **Branching model in practice**: work happens on a `dev` branch, then lands on `main` through a
   pull request (`Merge pull request #N from ajulthomas/dev`). That's the whole workflow —
   feature/fix on a branch, open a PR, merge. No need for anything heavier on a project this size.
2. **Commit messages as a debugging log**: "resolves build error due to multiple package
   managers" appearing twice is a real signal, not noise — it means the first fix didn't fully
   land, and it's exactly the kind of thing covered below.

Day-to-day commands used on this repo:

```bash
git clone <repo-url>
git checkout -b dev                 # or whatever branch you're working on
git status                          # check before anything destructive
git add main.py                     # stage specific files, not `git add .`
git commit -m "short, why-focused message"
git push -u origin dev
gh pr create --title "..." --body "..."   # or open the PR on GitHub
```

## Python development environment setup (venv, pip)

This repo currently has **two** dependency managers in play, which is exactly what caused the
"build error due to multiple package managers" commits above: a `pyproject.toml` (pip/PEP 621
style) *and* a `uv.lock` (the `uv` tool). Pick one path and stay on it for a given environment:

**Option A — plain venv + pip**

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e .
```

**Option B — uv (what this session used)**

```bash
uv venv          # creates .venv, respects pyproject.toml
uv sync          # installs locked dependencies from uv.lock
uv run chainlit run main.py   # run a command inside the managed env without activating it
```

Either way, `main.py` reads secrets from a local `.env` file via `python-dotenv` — this file is
already git-ignored (see `.gitignore`: `.venv` and `.env` are both excluded), so it never gets
committed. The two keys the app currently needs:

```
NVIDIA_API_KEY=nvapi-...
```

Running the app locally:

```bash
chainlit run main.py -w      # -w = auto-reload on file changes
```

...which matches what the `Procfile` does in production, just with a fixed host/port instead of
hot-reload:

```
web: chainlit run main.py --host 0.0.0.0 --port $PORT
```

**Takeaway for next week:** mixing `pyproject.toml` and `uv.lock` isn't wrong, but it only works if
contributors agree on one tool to install with. That ambiguity is itself a small architectural
decision that was never written down — a preview of why Week 2's "tech stack decisions" matter.
