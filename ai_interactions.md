# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Add a Retrieval-Augmented Generation (RAG) feature to the recommender: look up
relevant songs before answering a free-text question, fully integrated into
the main app (not a standalone script), with logging/guardrails, clear setup
steps, and a Mermaid system diagram.

**Prompts used:**

A single high-level prompt describing the RAG requirement, the
reproducibility/logging/guardrail requirements, and the system-diagram
deliverable. The agent asked one clarifying question (which Claude model to
use for cost reasons) before implementing.

**What did the agent generate or change?**

- `src/rag.py` (new): dependency-free TF-IDF retriever over song metadata,
  a Claude-based agent that answers only from retrieved songs, and guardrails
  (relevance threshold, missing-API-key fallback, per-exception-type error
  handling, logging to `logs/rag.log`).
- `src/main.py`: added `--ask`, `--interactive`, and a default RAG demo,
  wired into the existing CLI alongside the original profile scorer.
- `tests/test_rag.py` (new): retriever relevance tests plus LLM-call tests
  with the Anthropic client mocked (`pytest-mock`), so the suite runs without
  an API key or network access.
- `requirements.txt`, `.gitignore`, `README.md`: added `anthropic` and
  `pytest-mock`, ignored `logs/`, documented setup/usage.
- `diagrams/rag_system.mmd` (new): Mermaid system diagram.

**What did you verify or fix manually?**

Ran the test suite and the CLI by hand (`--ask`, no-API-key fallback, an
unrelated/nonsense query) to confirm the guardrails actually trigger instead
of just existing in code. The first retrieval draft scored "Night Drive Loop"
above the actual lofi/chill matches for a "late-night studying" query,
because song titles were part of the indexed text and "night" happened to
match the title; fixed by indexing bucketed feature descriptions (genre,
mood, energy/acousticness/valence/danceability/tempo turned into words)
instead of title/artist, and re-ran the query to confirm the fix.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
