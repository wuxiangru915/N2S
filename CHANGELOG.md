# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-09

### Added
- Natural-to-SQL agent with tool-calling and self-correction
- Data ingestion pipeline (CSV/Excel/JSON/Parquet to SQL database)
- Built-in Text2SQL benchmark with multi-provider comparison
- FastAPI demo server with web chat UI
- Docker support with one-command startup
- Multi-database support (SQLite, PostgreSQL, MySQL, DuckDB, and more)
- Multi-LLM support (OpenAI, Anthropic, Ollama, Agnes, Mimo, Mock)
- Agent memory with ChromaDB/Qdrant/FAISS backends

### Known Issues
- Demo UI uses placeholder image (`img/demo-placeholder.svg`)
- Legacy Vanna adapter has limited test coverage
