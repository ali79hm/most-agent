# MOST-Agent Project Master Checklist

This is the master roadmap for MOST-Agent. It is organized into
development phases with actionable tasks.

## Status legend

- [x] Completed
- [~] Decided / partially completed
- [ ] Not started
- [!] Blocked or needs verification

> Statuses reflect what has been discussed in the project conversations.
> A task should only be marked complete when it has been implemented
> and, where applicable, tested.

---

# Phase 0: Project definition and architecture

**Status: Architecture decisions underway**

- [x] Establish MOST-Agent as a local AI-powered movie and series
  assistant.
- [x] Decide to use IMDb IDs as external movie/series identifiers.
- [x] Decide every database record must have its own primary ID.
- [x] Decide `imdb_id` is unique but not the primary key.
- [x] Decide genres and countries are lists.
- [x] Decide to use a single `poster` field for artwork.
- [x] Decide to use dates where full dates are available and an
  integer year where only a year is known.
- [x] Define series runtime as typical episode runtime.
- [~] Establish the initial technology stack.
- [ ] Document the complete system architecture.
- [ ] Define the agent's capabilities and boundaries.
- [ ] Define the complete data flow, from IMDb data to the final
  answer.

**Phase completion:** A documented architecture explains how all
components communicate.

---

# Phase 1: Development environment and infrastructure

**Status: Started**

## 1.1 Development environment

- [x] Create the project directory.
- [x] Initialize Git.
- [x] Choose Python as the main development language.
- [x] Choose `uv` for Python environment and dependency management.
- [x] Choose Python 3.12.
- [ ] Establish the final Python project structure.
- [ ] Configure formatting and linting.
- [ ] Configure automated testing.
- [ ] Create development documentation.

## 1.2 Container infrastructure

- [x] Install Docker.
- [x] Set up Docker Compose.
- [x] Investigate Docker permissions.
- [~] Configure Docker access without requiring `sudo`.
- [x] Create initial LLM and embedding services.
- [!] Resolve NVIDIA GPU support in Docker.
- [ ] Verify container health checks.
- [ ] Finalize environment variables and `.env.example`.
- [ ] Test starting and stopping the complete infrastructure.

## 1.3 Model infrastructure

- [x] Compare Ollama and vLLM.
- [x] Choose `llama.cpp` for the LLM runtime.
- [x] Select the `llama.cpp` CUDA server image for the initial
  container setup.
- [x] Obtain Hugging Face access to EmbeddingGemma.
- [~] Configure Hugging Face authentication.
- [ ] Download and verify the LLM model.
- [ ] Download and verify the embedding model.
- [ ] Test LLM inference.
- [ ] Test embedding generation.
- [ ] Measure RAM and VRAM consumption.
- [ ] Measure inference speed.

**Important:** Distinguish the development setup from the eventual
installation on another computer. The final application should not
depend on the target computer already having Docker or a manually
installed vLLM environment.

**Phase completion:** The development infrastructure runs reliably and
both model services have been tested.

---

# Phase 2: Movie and series data model

**Status: Partially designed**

## 2.1 Entity design

- [x] Define movie records.
- [x] Define series records.
- [x] Define episode records.
- [~] Finalize season representation and relationships.
- [x] Give every record its own primary ID.
- [x] Make IMDb ID unique, not the primary key.
- [x] Keep `source_id` separate from IMDb ID.

## 2.2 Field decisions

- [x] Genre is a list.
- [x] Country is a list.
- [x] Use `poster` for artwork.
- [x] Use one poster image per record for now.
- [x] Use an integer year when only the year is available.
- [x] Use a date when the full date is available.
- [x] Define series runtime as typical episode runtime.
- [~] Finalize episode name and description.
- [~] Finalize episode rating representation.
- [ ] Finalize every remaining column and its data type.
- [ ] Define nullable fields and default values.
- [ ] Define database constraints.
- [ ] Define relationships and foreign keys.
- [ ] Create the final ER diagram.

## 2.3 Database implementation

- [ ] Translate the final schema into SQLAlchemy models.
- [ ] Create the initial database migration.
- [ ] Create all tables.
- [ ] Add primary and foreign keys.
- [ ] Add unique constraints.
- [ ] Add appropriate indexes.
- [ ] Test inserting, updating, and deleting records.
- [ ] Test relationships between series, seasons, and episodes.

**Phase completion:** The schema is finalized and implemented in
PostgreSQL, with working migrations and relationships.

---

# Phase 3: Movie data collection and ingestion

**Status: Not started**

## 3.1 Data source

- [ ] Identify the exact data provider or dataset.
- [ ] Establish how IMDb IDs will be used to retrieve records.
- [ ] Understand source API limits and licensing.
- [ ] Define the mapping between source fields and database fields.

## 3.2 Data ingestion

- [ ] Build a movie data importer.
- [ ] Build a series data importer.
- [ ] Build a season importer.
- [ ] Build an episode importer.
- [ ] Normalize genres.
- [ ] Normalize countries.
- [ ] Normalize dates and years.
- [ ] Handle missing information.
- [ ] Validate incoming records.
- [ ] Prevent duplicate IMDb records.
- [ ] Implement database upserts.

## 3.3 Poster management

- [ ] Retrieve poster URLs.
- [ ] Decide whether posters remain remote URLs or are downloaded
  locally.
- [ ] Handle broken poster URLs.
- [ ] Handle missing posters.
- [ ] Verify poster paths and formats.

## 3.4 Data quality

- [ ] Check duplicate records.
- [ ] Check invalid dates.
- [ ] Check missing IMDb IDs.
- [ ] Check incorrect relationships.
- [ ] Check incomplete episodes.
- [ ] Build a data validation report.

**Phase completion:** IMDb IDs can be used to reliably populate the
database with movie and series records.

---

# Phase 4: PostgreSQL and vector database

**Status: Technology selected, implementation pending**

## 4.1 PostgreSQL

- [~] Choose PostgreSQL as the main database.
- [~] Choose PostgreSQL with the `pgvector` extension instead of
  introducing a separate vector database initially.
- [ ] Configure PostgreSQL.
- [ ] Install and enable `pgvector`.
- [ ] Connect PostgreSQL to Python.
- [ ] Implement database connection management.
- [ ] Implement transactions.
- [ ] Test database persistence.

## 4.2 Vector storage

- [ ] Decide which entities need embeddings.
- [ ] Determine embedding dimensions from the selected model.
- [ ] Create embedding columns.
- [ ] Associate each embedding with its corresponding movie or series.
- [ ] Store embedding model/version information.
- [ ] Implement vector insertion and updates.
- [ ] Implement cosine similarity queries.
- [ ] Test exact nearest-neighbor searches.
- [ ] Evaluate HNSW indexing when the dataset grows.
- [ ] Benchmark query performance.

**Phase completion:** PostgreSQL handles both normal catalog queries and
vector similarity searches successfully.

---

# Phase 5: Embedding system

**Status: Learning and experimentation**

## 5.1 Model preparation

- [x] Explore EmbeddingGemma.
- [x] Obtain Hugging Face access.
- [~] Investigate the embedding service setup.
- [x] Learn what TEI is.
- [ ] Finalize the embedding runtime.
- [ ] Verify model compatibility with the runtime.
- [ ] Verify embedding dimensions.
- [ ] Benchmark embedding generation.

## 5.2 Text preparation

- [ ] Decide which movie fields contribute to embeddings.
- [ ] Create a consistent text representation for each movie.
- [ ] Create a text representation for series.
- [ ] Decide how episodes will be represented.
- [ ] Handle missing descriptions.
- [ ] Handle long text and token limits.

## 5.3 Embedding generation

- [ ] Build an embedding generation module.
- [ ] Generate embeddings for existing records.
- [ ] Store embeddings in PostgreSQL.
- [ ] Implement batch processing.
- [ ] Implement automatic embedding updates when records change.
- [ ] Avoid generating duplicate embeddings unnecessarily.
- [ ] Track model versions.
- [ ] Test similarity between related movies.

## 5.4 Vector fundamentals

- [x] Understand what vectors are.
- [x] Learn NumPy's linear algebra module.
- [x] Learn vector operations.
- [x] Learn cosine similarity fundamentals.
- [ ] Understand normalization in practical embedding workflows.
- [ ] Understand cosine distance versus cosine similarity.
- [ ] Understand nearest-neighbor search.
- [ ] Understand HNSW at a conceptual level.

**Phase completion:** Movie information can be converted into
embeddings, stored, and retrieved by semantic similarity.

---

# Phase 6: Search and retrieval engine

**Status: Not started**

## 6.1 Traditional search

- [ ] Search by movie title.
- [ ] Search by IMDb ID.
- [ ] Filter by genre.
- [ ] Filter by country.
- [ ] Filter by release year or date.
- [ ] Filter by runtime.
- [ ] Filter by IMDb rating.
- [ ] Filter by movie versus series.
- [ ] Support multiple filters together.

## 6.2 Semantic search

- [ ] Convert the user's query into an embedding.
- [ ] Search for similar movie embeddings.
- [ ] Retrieve the most relevant candidates.
- [ ] Implement similarity thresholds.
- [ ] Return similarity scores.
- [ ] Test semantic searches with different descriptions.

## 6.3 Hybrid search

- [ ] Combine traditional database filters with semantic search.
- [ ] Add PostgreSQL full-text search.
- [ ] Combine lexical and vector results.
- [ ] Investigate Reciprocal Rank Fusion.
- [ ] Implement result ranking.
- [ ] Evaluate whether a reranker is necessary.
- [ ] Benchmark retrieval quality.

**Example expected behavior:**

User: "Find me a movie about artificial intelligence becoming dangerous,
preferably sci-fi, released after 2015."

The retrieval system should:

1. Understand the genre and year constraints.
2. Search semantically for the story concept.
3. Filter results using database fields.
4. Rank the remaining candidates.
5. Return relevant movies.

**Phase completion:** The retrieval engine understands both explicit
filters and natural-language descriptions.

---

# Phase 7: Agent brain and orchestration

**Status: Not started**

## 7.1 LLM integration

- [x] Select `llama.cpp` as the initial LLM runtime.
- [ ] Download and configure the final LLM.
- [ ] Connect Python to the LLM server.
- [ ] Implement a reusable LLM client.
- [ ] Handle timeouts and errors.
- [ ] Support streaming responses if needed.
- [ ] Test structured JSON responses.

## 7.2 Intent understanding

- [ ] Understand movie recommendation requests.
- [ ] Understand movie search requests.
- [ ] Understand similar-movie requests.
- [ ] Extract genres.
- [ ] Extract countries.
- [ ] Extract years and dates.
- [ ] Extract runtime constraints.
- [ ] Extract rating constraints.
- [ ] Identify missing or ambiguous information.

## 7.3 Agent tools

- [ ] Build a movie search tool.
- [ ] Build a series search tool.
- [ ] Build a semantic search tool.
- [ ] Build a recommendation tool.
- [ ] Build a movie detail retrieval tool.
- [ ] Build a similar-movie tool.
- [ ] Define tool input and output schemas.
- [ ] Implement tool validation.
- [ ] Handle tool execution errors.

## 7.4 Agent orchestration

- [ ] Design the agent execution loop.
- [ ] Decide when the LLM should call tools.
- [ ] Execute the selected tools.
- [ ] Return tool results to the LLM.
- [ ] Generate final answers from actual results.
- [ ] Prevent the LLM from inventing database records.
- [ ] Handle multi-step requests.
- [ ] Implement conversation context.

**Phase completion:** A user can communicate naturally with MOST-Agent,
and the agent can select and execute the correct tools.

---

# Phase 8: Recommendation engine

**Status: Not started**

- [ ] Define recommendation criteria.
- [ ] Implement content-based recommendations.
- [ ] Recommend movies similar to a selected movie.
- [ ] Combine genre similarity and semantic similarity.
- [ ] Incorporate IMDb ratings where appropriate.
- [ ] Incorporate user preferences.
- [ ] Avoid recommending the same results repeatedly.
- [ ] Explain why each movie was recommended.
- [ ] Evaluate recommendation quality.
- [ ] Compare recommendations against manually selected examples.

## Later possibilities

- [ ] Collaborative filtering.
- [ ] Personalized user profiles.
- [ ] Watch history.
- [ ] User feedback.
- [ ] Recommendation adaptation.

**Phase completion:** MOST-Agent can generate relevant recommendations
and explain why each result was selected.

---

# Phase 9: Backend and application architecture

**Status: Not started**

## 9.1 Backend

- [ ] Choose the backend framework.
- [ ] Design the application service architecture.
- [ ] Create API endpoints.
- [ ] Implement movie endpoints.
- [ ] Implement series endpoints.
- [ ] Implement search endpoints.
- [ ] Implement agent/chat endpoints.
- [ ] Implement recommendation endpoints.
- [ ] Add request validation.
- [ ] Add error handling.
- [ ] Add logging.

## 9.2 Application architecture

- [ ] Separate database logic from business logic.
- [ ] Separate LLM integration from agent logic.
- [ ] Separate retrieval from recommendation logic.
- [ ] Implement dependency management.
- [ ] Implement configuration management.
- [ ] Ensure components can be tested independently.

**Phase completion:** The application has a clean, maintainable backend
with working APIs.

---

# Phase 10: User interface

**Status: Not started**

The exact UI technology is still undecided.

- [ ] Decide whether the first interface is a web application or
  desktop application.
- [ ] Design the chat interface.
- [ ] Implement conversation history.
- [ ] Display movie results.
- [ ] Display posters.
- [ ] Display movie details.
- [ ] Display recommendation explanations.
- [ ] Support movie and series filters.
- [ ] Display loading states.
- [ ] Handle errors.
- [ ] Connect the UI to the backend.

**Phase completion:** A user can comfortably interact with MOST-Agent.

---

# Phase 11: Testing and evaluation

**Status: Not started**

## 11.1 Unit tests

- [ ] Test database models.
- [ ] Test database operations.
- [ ] Test data ingestion.
- [ ] Test embedding generation.
- [ ] Test similarity calculations.
- [ ] Test retrieval.
- [ ] Test agent tools.
- [ ] Test API endpoints.

## 11.2 Integration tests

- [ ] Test PostgreSQL integration.
- [ ] Test LLM integration.
- [ ] Test embedding integration.
- [ ] Test retrieval and LLM together.
- [ ] Test the complete agent workflow.
- [ ] Test failure scenarios.

## 11.3 Quality evaluation

- [ ] Create a set of representative user queries.
- [ ] Measure search relevance.
- [ ] Measure recommendation quality.
- [ ] Measure retrieval speed.
- [ ] Measure LLM response time.
- [ ] Test incorrect and ambiguous queries.
- [ ] Check for hallucinated movie information.
- [ ] Test with a larger dataset.

**Phase completion:** There is measurable evidence that MOST-Agent works
correctly and reliably.

---

# Phase 12: Packaging and deployment

**Status: Not started**

The target computer should not require Docker or a manually installed
vLLM environment.

## 12.1 Local runtime

- [ ] Design the local installation architecture.
- [ ] Package the Python application.
- [ ] Package or install the `llama.cpp` runtime.
- [ ] Configure CPU inference.
- [ ] Add optional GPU acceleration.
- [ ] Configure model storage.
- [ ] Configure PostgreSQL installation.
- [ ] Ensure pgvector is available on the target machine.
- [ ] Configure local model paths.
- [ ] Configure application startup.

## 12.2 Installation

- [ ] Create an installation process.
- [ ] Implement first-run configuration.
- [ ] Handle model downloads.
- [ ] Handle missing dependencies.
- [ ] Handle insufficient RAM or VRAM.
- [ ] Test on a clean computer.
- [ ] Test without Docker.
- [ ] Test without NVIDIA drivers.
- [ ] Test on supported operating systems.

## 12.3 Reliability

- [ ] Implement database backup.
- [ ] Implement database restoration.
- [ ] Implement application updates.
- [ ] Implement model updates.
- [ ] Implement startup health checks.
- [ ] Implement error logging.

**Phase completion:** MOST-Agent can be installed and used on another
computer without requiring the development environment.

---

# Phase 13: Documentation and release

**Status: Not started**

- [ ] Write installation instructions.
- [ ] Write architecture documentation.
- [ ] Document database schema.
- [ ] Document API endpoints.
- [ ] Document configuration options.
- [ ] Document model requirements.
- [ ] Write troubleshooting instructions.
- [ ] Prepare a release version.
- [ ] Create a release checklist.
- [ ] Tag the first stable Git version.

---

# Overall project progress

The following is a qualitative assessment based on project discussions,
not a measured percentage of completed code.

  Phase                            Current status
  -------------------------------- ------------------------------
  0\. Architecture                 Decisions underway
  1\. Infrastructure               Started
  2\. Data model                   Partially designed
  3\. Data ingestion               Not started
  4\. PostgreSQL / pgvector        Technology selected
  5\. Embeddings                   Learning and experimentation
  6\. Search and retrieval         Not started
  7\. Agent orchestration          Not started
  8\. Recommendations              Not started
  9\. Backend                      Not started
  10\. User interface              Not started
  11\. Testing                     Not started
  12\. Deployment                  Not started
  13\. Documentation and release   Not started

---

# Recommended next steps

Work through the project in this order:

1. **Finish Phase 1:** Resolve the NVIDIA/Docker issue, verify the
  model services, and make sure inference works.
2. **Finish Phase 2:** Finalize the complete database schema, including
  movies, series, seasons, and episodes.
3. **Start Phase 3:** Decide on the data source and build the ingestion
  pipeline.
4. **Start Phase 4:** Implement PostgreSQL and pgvector.
5. **Continue toward the first MVP:** Build embeddings, retrieval, and
  the agent before spending time on the UI.

## Project working rules

- Work through the roadmap phase by phase.
- Update this checklist whenever a task is completed or an
  architectural decision changes.
- Do not mark a task complete just because it has been discussed;
  implementation and testing are required where applicable.
- Record important architectural decisions so later phases remain
  consistent.
- Revisit earlier decisions when new technical evidence justifies a
  change.
