<div align="center">

# N2S — Natural-to-SQL Agent

**Turn natural language into SQL, execute it, and visualise results.**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?logo=opensourceinitiative&logoColor=white)](./LICENSE)
[![Tests](https://img.shields.io/badge/Tests-184%20passed-success)](#commands)

[English](README.md) | [中文](README_CN.md)

</div>

N2S is a natural-language-to-SQL agent built on [Vanna](https://github.com/vanna-ai/vanna) 2.0. It inspects the database schema, generates SQL, executes it, and visualises the results — retrying automatically when SQL fails.

> Derivative project. Retains Vanna's MIT license and copyright notices, see [NOTICE](./NOTICE).

## Features

- **Tool-calling agent loop** — schema introspection → SQL generation → execution → visualisation; failed SQL is fed back to the LLM for retry
- **Data ingestion pipeline** — scan a directory of CSV/Excel/JSON/Parquet files, auto-infer schema, load into the target database (LLM-assisted schema enhancement with graceful fallback)
- **Multi-database** — SQLite, PostgreSQL, MySQL, DuckDB, ClickHouse, Oracle, BigQuery, Snowflake, MSSQL, Hive, Presto via SQLAlchemy
- **Multi-LLM** — OpenAI, Anthropic, Gemini, Ollama, or any OpenAI-compatible endpoint (Agnes, Mimo); built-in `mock` for key-less demos
- **Built-in Text2SQL benchmark** — reproducible evaluation across providers (`python -m n2s.eval`)

## Quick Start

Requires Python 3.9+. The web UI bundle is committed to the repo — no Node.js needed.

```bash
git clone https://github.com/wuxiangru915/N2S.git
cd N2S
pip install -e ".[fastapi]"
python n2s_app.py    # open http://localhost:8000
```

The default `mock` provider answers canned questions against the bundled demo database (`employees`). For arbitrary questions, point `N2S_LLM_PROVIDER` at a real LLM:

```bash
export N2S_LLM_PROVIDER=agnes
export AGNES_API_KEY=...
export AGNES_BASE_URL=https://api.deepseek.com/v1   # any OpenAI-compatible endpoint
export AGNES_MODEL=deepseek-chat
python n2s_app.py
```

Other providers (`openai`, `anthropic`, `gemini`, `ollama`, `mimo`) and their env vars are listed in [`.env.example`](.env.example) and the table below.

## Architecture

```
                           N2S Architecture
 ┌──────────────────────────────────────────────────────────────────┐
 │                         User Interface                           │
 │            (Web Chat / CLI / FastAPI / Flask)                    │
 └────────────────────────────┬─────────────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                        N2S Agent Core                            │
 │  ┌──────────┐  ┌───────────────┐  ┌───────────────────────────┐ │
 │  │  Agent   │  │ Tool Registry │  │   Workflow Handler        │ │
 │  │  Loop    │──│  (tool-call)  │  │ (/help, /status, /mem)   │ │
 │  └────┬─────┘  └───────┬───────┘  └───────────────────────────┘ │
 │       │                │                                         │
 │       │    ┌───────────┼───────────┐                            │
 │       │    ▼           ▼           ▼                            │
 │       │  Schema     RunSQL    Visualize                        │
 │       │  Tool       Tool      Data Tool                         │
 │       └─────────────────────────────────┘                        │
 └──────────────────────────────────────────────────────────────────┘
                   │                    │                    │
                   ▼                    ▼                    ▼
        ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
        │  LLM Providers   │  │  Databases   │  │  Vector Memory   │
        │  (OpenAI,        │  │  (SQLite,    │  │  (ChromaDB,      │
        │   Anthropic,     │  │   Postgres,  │  │   FAISS,         │
        │   Gemini,        │  │   MySQL,     │  │   Qdrant,        │
        │   Ollama...)     │  │   DuckDB...) │  │   Pinecone...)   │
        └──────────────────┘  └──────────────┘  └──────────────────┘
```

## Agent Workflow

```
User Question
    │
    ▼
┌─────────────────┐
│  Parse Input    │  ← Workflow handler checks for /help, /status, etc.
└────────┬────────┘
         │ (not a command)
         ▼
┌─────────────────┐
│  Build Context  │  ← Load conversation history + agent memory
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────────────┐
│  Call LLM       │────▶│  LLM returns tool call? │
└────────┬────────┘     └───────────┬─────────────┘
         │                          │
         │              ┌───────────┴───────────┐
         │              │                       │
         │         Yes  ▼                  No   ▼
         │     ┌──────────────┐      ┌──────────────┐
         │     │ Execute Tool │      │ Return Final │
         │     │ (SQL/Schema/ │      │   Response   │
         │     │  Visualize)  │      └──────────────┘
         │     └──────┬───────┘
         │            │
         │            ▼
         │     ┌──────────────┐
         │     │ SQL Failed?  │
         │     └──────┬───────┘
         │            │
         │     ┌──────┴───────┐
         │     │              │
         │  Yes▼          No  ▼
         │  Feed error    Append result
         │  back to LLM   to context
         │      │              │
         └──────┴──────────────┘
                (loop back to Call LLM,
                 up to max_tool_calls)
```

## Data Ingestion Pipeline

```
Directory / File
    │
    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Scanner    │────▶│    Reader    │────▶│   Inferrer   │
│ (classify    │     │ (CSV/Excel/  │     │ (auto-detect │
│  file types) │     │  JSON/Parquet)│     │  schema+type)│
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                    │                           │
                               LLM available?              Not available
                                    │                           │
                                    ▼                           ▼
                           ┌──────────────┐          ┌──────────────┐
                           │  LLM Enhancer│          │  Fallback:   │
                           │ (enrich table│          │  use inferred │
                           │  & column    │          │  schema only  │
                           │  descriptions)│         └──────┬───────┘
                           └──────┬───────┘                 │
                                  └──────────┬──────────────┘
                                             ▼
                                    ┌──────────────┐
                                    │    Loader    │
                                    │ (to_sql into │
                                    │  target DB)  │
                                    └──────────────┘
```

## Screenshots

### Login

![Login](img/n2s-login.png)

### Chat & data visualisation

![Chat](img/n2s-chat.png)

## Commands

| Command | Description |
|---------|-------------|
| `python n2s_app.py` | Demo server (FastAPI + Web UI), port 8000 |
| `python -m n2s.eval --providers openai anthropic gemini` | Text2SQL benchmark on the bundled dataset |
| `python -m n2s.eval --dataset <yaml> --providers <...>` | Benchmark on a custom dataset |
| `pytest tests/ -m "not integration and not anthropic and not openai and not azureopenai and not gemini and not ollama and not postgres and not mysql and not slow"` | Unit tests (184 passed) |

## Supported LLM Providers

| Provider | Type | API key | Status |
|----------|------|---------|--------|
| `mock` | built-in | no | ✅ verified |
| `agnes` | OpenAI-compatible | yes | ✅ verified |
| `openai` | cloud | yes | ✅ verified |
| `gemini` | cloud | yes | ✅ verified |
| `anthropic` | cloud | yes | code present |
| `mimo` | OpenAI-compatible | yes | code present |
| `ollama` | local | no | code present |

## Supported Databases (via SQLAlchemy)

| Database | Status |
|----------|--------|
| SQLite, PostgreSQL, MySQL | ✅ verified |
| DuckDB, ClickHouse, Oracle, BigQuery, Snowflake, MSSQL, Hive, Presto | code present, untested |

## Project Structure

```
n2s/
├── src/n2s/
│   ├── core/              # Agent framework (agent, llm, tools, workflow, components)
│   ├── capabilities/      # Capability interfaces (sql_runner, agent_memory, file_system)
│   ├── components/        # UI components (rich + simple)
│   ├── integrations/      # DB/LLM/vector store integrations
│   │   ├── anthropic/     #   Anthropic Claude
│   │   ├── openai/        #   OpenAI GPT
│   │   ├── google/        #   Google Gemini
│   │   ├── ollama/        #   Local Ollama
│   │   ├── sqlite/        #   SQLite runner
│   │   ├── postgres/      #   PostgreSQL runner
│   │   ├── chromadb/      #   ChromaDB vector memory
│   │   └── ...            #   20+ more integrations
│   ├── ingest/            # Data ingestion pipeline
│   ├── demo/              # Demo server, agent, database manager
│   ├── eval/              # Text2SQL benchmark evaluation
│   ├── examples/          # Example scripts
│   ├── servers/           # FastAPI / Flask / CLI servers
│   └── tools/             # Built-in tools (run_sql, visualize_data, file_system)
├── frontends/webcomponent/# TypeScript web components (Vite + Storybook)
├── tests/                 # Pytest test suite
├── n2s_app.py             # Demo entry point
├── pyproject.toml         # Project metadata + dependencies
├── docker-compose.yml     # Docker deployment
└── .env.example           # Environment variable template
```

## License

[MIT](./LICENSE)
