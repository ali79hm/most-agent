# MOST-Agent — Project Roadmap

> **Status (2026-11-20):** Phases 0–4 complete; Phase 5 Steps 5.1–5.3 verified. Current: Step 5.4 (implementation proposed; awaiting verification).
>
> **Scope:** A self-hosted assistant for a personal movie, series, and episode library. It uses local LLM and embedding inference, PostgreSQL + pgvector, conversation memory, agent execution history, and a web interface. External LLM providers may be added as an option.
>
> **Project root:** All paths in this roadmap are relative to the `most-agent/` repository root. The Python package is `most_agent/`; there is no `src/` directory.
>
> **Companion context:** Read `MOST_AGENT_PHASE0_SUMMARY.md` before continuing in a new chat.

## Phase 0 of 10 — Project foundation (11/11)

- [x] **0.1** Initialize MOST-Agent project, Git, Python and uv.
- [x] **0.2** Verify Docker, Compose and GPU setup.
- [x] **0.3** Set up local Qwen model with llama.cpp.
- [x] **0.4** Set up local EmbeddingGemma with TEI.
- [x] **0.5** Verify LLM and embedding server health.
- [x] **0.6** Test LLM completion, streaming and request history.
- [x] **0.7** Test vectors, similarity, batching and semantic search.
- [x] **0.8** Set up PostgreSQL, pgvector and Python database connection.
- [x] **0.9** Design media schema, implement ORM models and run initial Alembic migration.
- [x] **0.10** Run a combined database smoke test with movie, series, episode and embedding records.
- [x] **0.11** Finalize core project configuration and startup documentation. Git staging, commits and `.gitignore` preferences remain developer-managed.

## Phase 1 of 10 — MOST-Brain data integration (revised scope; complete)

> **Scope change:** MOST-Brain and MOST-Agent share the same PostgreSQL database directly. The original JSON import/upsert workflow was superseded; it was **not** separately implemented or verified as originally written.

- [x] **1.1–1.4 (revised deliverable)** Reuse the shared PostgreSQL schema and application database sessions; seed mock movie/series/episode records and verify access for subsequent retrieval work.

Original plan, retained here for reference (superseded): define a MOST-Brain JSON contract; import/upsert by IMDb ID; link episodes and handle updates; build a repeatable import command and report.

## Phase 2 of 10 — Embeddings and retrieval

- [x] **2.1** Build consistent search text for movies and series; leave episode embeddings empty initially.
- [x] **2.2** Generate and store embeddings in batches; re-embed changed content only.
- [x] **2.3** Implement metadata filters and pgvector top-K similarity search.
- [x] **2.4** Add hybrid search (text + vector) and indexes when justified by measurements.

## Phase 3 of 10 — LLM provider layer

- [x] **3.1** Create a provider interface for local llama.cpp and external API models.
- [x] **3.2** Add configurable model selection, prompts, timeouts and streaming.
- [x] **3.3** Normalize provider errors and track token usage and latency.

## Phase 4 of 10 — Conversations and history

- [x] **4.1** Implement conversation and message tables with Alembic.
- [x] **4.2** Save messages and load history using a conversation ID.
- [x] **4.3** Manage context-window limits with trimming or summarization.
- [x] **4.4** Test multiple conversations and correct history isolation.

## Phase 5 of 10 — LangGraph state and persistence (in progress)

- [x] **5.1** Build the first LangGraph workflow with typed state.
- [x] **5.2** Add PostgreSQL checkpoints and stable thread IDs.
- [x] **5.3** Resume a conversation across separate HTTP requests and restarts.
- [x] **5.4** Distinguish user-visible messages from checkpoints and agent state.

## Phase 6 of 10 — Agent tools and workflows

- [ ] **6.1** Implement tools for title lookup, metadata filters and similar-media search.
- [ ] **6.2** Let the agent choose tools and produce grounded answers from retrieved records.
- [ ] **6.3** Handle follow-up questions, no-result cases and invalid tool arguments.
- [ ] **6.4** Add episode-level semantic search when its embeddings are populated.

## Phase 7 of 10 — Execution traces and observability

- [ ] **7.1** Record each agent run, model call, tool call and duration.
- [ ] **7.2** Make graph execution paths inspectable per conversation/run.
- [ ] **7.3** Capture errors, retrieval results and basic quality metrics safely.

## Phase 8 of 10 — API and user interface

- [ ] **8.1** Build FastAPI endpoints for chat, streaming, conversations and media search.
- [ ] **8.2** Evaluate an existing open-source chat frontend and integrate it if suitable.
- [ ] **8.3** Otherwise implement a small web UI with conversation history and streamed responses.
- [ ] **8.4** Expose useful run/tool details for learning and debugging.

## Phase 9 of 10 — Tests and evaluation

- [ ] **9.1** Add focused unit and integration tests for ingestion, retrieval and chat.
- [ ] **9.2** Create a small movie/series question set and evaluate search relevance.
- [ ] **9.3** Test persistence, model-provider switching and failure handling.
- [ ] **9.4** Measure latency, memory usage and throughput on the home PC.

## Phase 10 of 10 — Packaging and deployment

- [ ] **10.1** Containerize MOST-Agent and finalize Docker Compose services and volumes.
- [ ] **10.2** Provide first-run configuration, migrations and model setup instructions.
- [ ] **10.3** Add database backups, restore instructions and basic security defaults.
- [ ] **10.4** Test installation and operation on another home PC without a dedicated server.
- [ ] **10.5** Tag the first usable release and document remaining improvements.

---

## Architecture decisions (confirmed during Phases 3–5)

- Application-owned system prompt: system messages are not written through the conversation service. LLM requests add one leading application system prompt. The existing database constraint still permits legacy/direct SQL `system` rows; no schema migration has been applied to prohibit those.
- `conversations` and `conversation_messages` are authoritative for user-visible dialogue. LangGraph checkpoints store execution state and may temporarily duplicate prepared messages; they are not the canonical transcript.
- Step 5.3 was verified across separate Python processes: a completed user/assistant turn was stored atomically and subsequently reloaded. It does not yet guarantee exactly-once processing for interrupted or concurrent requests.
- Capture of exact serialized LLM requests and responses remains planned for Phase 7.

---

## Progress rules

- Check a step only after its main deliverable works.
- Prefer one meaningful verification per step; avoid unnecessary micro-checkpoints.
- Stay on the current step until the user approves continuing.
- If a requirement changes a roadmap step, update this file and explicitly tell the user what changed.
- Do not create extra checkpoints for routine commands or tests.
- Use paths relative to the `most-agent/` project root.
- The user is a developer: explain meaningful design choices and file changes, but do not over-explain routine Git or shell operations.
