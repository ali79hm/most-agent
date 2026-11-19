# MOST-Agent

MOST-Agent is a local-first AI assistant for searching, exploring,
and recommending movies and TV series in your personal media library.

## Technology Stack

- Python 3.12+
- uv - Python dependency management
- llama.cpp - Local LLM inference
- Qwen3.5-2B - Language model
- Hugging Face TEI - Embedding inference
- EmbeddingGemma-300M - Embedding model
- PostgreSQL 17
- pgvector - Vector similarity search
- SQLAlchemy - ORM
- Alembic - Database migrations
- FastAPI - API framework
- LangGraph - Agent orchestration

## Requirements

- Python 3.12+
- uv
- Docker
- Docker Compose
- NVIDIA GPU and NVIDIA Container Toolkit
  for the current CUDA-enabled LLM configuration

## Project Structure

```text
most-agent/
├── migrations/
├── models/
├── most_agent/
│   └── db/
│       └── models/
├── experiments/
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
└── README.md