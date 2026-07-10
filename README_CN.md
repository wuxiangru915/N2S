<div align="center">

# N2S — 自然语言转 SQL 智能体

**将自然语言转换为 SQL，执行查询，并可视化结果。**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?logo=opensourceinitiative&logoColor=white)](./LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?logo=github)](./CONTRIBUTING.md)
[![Tests](https://img.shields.io/badge/Tests-184%20passed-success)](#测试)

[English](README.md) | [中文](README_CN.md)

</div>

---

N2S 是一个开源的**自然语言转 SQL**智能体。基于 [Vanna](https://github.com/vanna-ai/vanna) 2.0 智能体框架构建，在原版基础上增强了工具调用、多轮推理、数据导入管道和内置 Text2SQL 基准测试。

> N2S 是衍生项目，保留了 Vanna 的 MIT 许可证和所有原始版权声明。归属信息详见 [NOTICE](./NOTICE)。

## 功能特性

- **智能体 + 工具调用** — 智能体推理数据库 schema，生成 SQL，执行查询，并通过工具循环可视化结果。
- **自动纠错** — SQL 执行失败时，错误信息会反馈给 LLM 进行自动重试。
- **Schema 内省** — 智能体在编写查询前先检查数据库结构，降低幻觉风险。
- **数据导入管道** — 扫描目录，读取 CSV/Excel/JSON/Parquet 文件，自动推断 schema，加载到目标数据库。支持 LLM 辅助 schema 增强，LLM 不可用时自动降级。
- **多数据库支持** — SQLite、PostgreSQL、MySQL、DuckDB、ClickHouse、Oracle、BigQuery、Snowflake、MSSQL、Hive、Presto 等，通过 SQLAlchemy 统一接入。
- **多 LLM 提供商** — Mock（无需 API Key）、OpenAI、Anthropic、Gemini、Ollama、以及 OpenAI 兼容端点（Agnes、Mimo）。
- **内置基准测试** — `python -m n2s.eval` 运行可复现的 Text2SQL 评测，对比多个 LLM 提供商。
- **一键启动 Demo** — `python n2s_app.py` 启动带 Web UI 的 FastAPI 服务器。

## 截图

### 登录与控制面板

![登录页面](img/n2s-login.png)

### 聊天界面

![聊天界面](img/n2s-chat.png)

## 快速开始

### 1. 安装

```bash
git clone https://github.com/YOUR_USERNAME/n2s.git
cd n2s
pip install -e ".[fastapi]"
```

### 2. 运行 Mock Demo（无需 API Key）

```bash
python n2s_app.py
# 打开 http://localhost:8000
```

### 3. 使用真实 LLM

支持的提供商：`mock`（默认）、`agnes`、`openai`、`anthropic`、`ollama`、`mimo`。

```bash
# OpenAI
export N2S_LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
python n2s_app.py

# Anthropic
export N2S_LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python n2s_app.py

# Ollama（本地）
export N2S_LLM_PROVIDER=ollama
export OLLAMA_MODEL=llama3.1
python n2s_app.py
```

### 4. Docker 部署

```bash
docker-compose up --build
# 打开 http://localhost:8000
```

## 架构图

```
                           N2S 架构图
 ┌──────────────────────────────────────────────────────────────────┐
 │                           用户界面                               │
 │                (Web 聊天 / CLI / FastAPI / Flask)                │
 └────────────────────────────┬─────────────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                       N2S 智能体核心                             │
 │  ┌──────────┐  ┌───────────────┐  ┌───────────────────────────┐ │
 │  │  Agent   │  │  工具注册表   │  │    工作流处理器            │ │
 │  │  循环    │──│  (工具调用)   │  │ (/help, /status, /mem)   │ │
 │  └────┬─────┘  └───────┬───────┘  └───────────────────────────┘ │
 │       │                │                                         │
 │       │    ┌───────────┼───────────┐                            │
 │       │    ▼           ▼           ▼                            │
 │       │  Schema     RunSQL    Visualize                        │
 │       │  工具       工具       数据可视化工具                    │
 │       └─────────────────────────────────┘                        │
 └──────────────────────────────────────────────────────────────────┘
                   │                    │                    │
                   ▼                    ▼                    ▼
        ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
        │   LLM 提供商     │  │   数据库     │  │   向量记忆       │
        │  (OpenAI,        │  │  (SQLite,    │  │  (ChromaDB,      │
        │   Anthropic,     │  │   Postgres,  │  │   FAISS,         │
        │   Gemini,        │  │   MySQL,     │  │   Qdrant,        │
        │   Ollama...)     │  │   DuckDB...) │  │   Pinecone...)   │
        └──────────────────┘  └──────────────┘  └──────────────────┘
```

## 智能体工作流

```
用户提问
    │
    ▼
┌─────────────────┐
│   解析输入      │  ← 工作流处理器检查 /help, /status 等命令
└────────┬────────┘
         │ (非命令)
         ▼
┌─────────────────┐
│   构建上下文    │  ← 加载对话历史 + 智能体记忆
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────────────┐
│   调用 LLM      │────▶│  LLM 返回工具调用?      │
└────────┬────────┘     └───────────┬─────────────┘
         │                          │
         │              ┌───────────┴───────────┐
         │              │                       │
         │          是  ▼                  否   ▼
         │     ┌──────────────┐      ┌──────────────┐
         │     │  执行工具    │      │  返回最终    │
         │     │ (SQL/Schema/ │      │    响应      │
         │     │  可视化)     │      └──────────────┘
         │     └──────┬───────┘
         │            │
         │            ▼
         │     ┌──────────────┐
         │     │ SQL 执行失败?│
         │     └──────┬───────┘
         │            │
         │     ┌──────┴───────┐
         │     │              │
         │   是▼           否 ▼
         │  错误反馈       结果追加到
         │  给 LLM 重试    上下文
         │      │              │
         └──────┴──────────────┘
                (回到调用 LLM，
                 不超过最大工具调用次数)
```

## 数据导入流程

```
目录 / 文件
    │
    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    扫描器    │────▶│    读取器    │────▶│   推断器     │
│ (分类文件    │     │ (CSV/Excel/  │     │ (自动检测    │
│  类型)       │     │  JSON/Parquet)│    │  schema+类型)│
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                    │                           │
                               LLM 可用?                   不可用
                                    │                           │
                                    ▼                           ▼
                           ┌──────────────┐          ┌──────────────┐
                           │  LLM 增强器  │          │  降级方案:   │
                           │ (丰富表和    │          │  仅使用推断  │
                           │  列描述)     │          │  的 schema   │
                           └──────┬───────┘          └──────┬───────┘
                                  └──────────┬──────────────┘
                                             ▼
                                    ┌──────────────┐
                                    │    加载器    │
                                    │ (to_sql 写入 │
                                    │  目标数据库) │
                                    └──────────────┘
```

## 基准测试

在 Text2SQL 数据集上评估 N2S：

```bash
python -m n2s.eval \
  --dataset src/n2s/eval/datasets/n2s_sql.yaml \
  --providers mock openai anthropic
```

报告包含以下指标：

| 指标 | 说明 |
|------|------|
| Trajectory（轨迹） | 智能体是否调用了预期的工具 |
| Output（输出） | 最终回答是否包含预期关键词 |
| SQL Similarity（SQL 相似度） | 生成的 SQL 是否匹配参考 SQL |
| SQL Execution（SQL 执行） | SQL 执行后是否返回预期结果 |

## 测试

```bash
# 运行所有单元测试（不含需要 API Key 的集成测试）
pytest tests/ -m "not integration and not anthropic and not openai and not azureopenai and not gemini and not ollama and not postgres and not mysql and not slow"
```

## 项目结构

```
n2s/
├── src/n2s/
│   ├── core/              # 智能体框架（agent, llm, tools, workflow, components）
│   ├── capabilities/      # 能力接口（sql_runner, agent_memory, file_system）
│   ├── components/        # UI 组件（rich + simple）
│   ├── integrations/      # 数据库/LLM/向量存储集成
│   │   ├── anthropic/     #   Anthropic Claude
│   │   ├── openai/        #   OpenAI GPT
│   │   ├── google/        #   Google Gemini
│   │   ├── ollama/        #   本地 Ollama
│   │   ├── sqlite/        #   SQLite runner
│   │   ├── postgres/      #   PostgreSQL runner
│   │   ├── chromadb/      #   ChromaDB 向量记忆
│   │   └── ...            #   20+ 其他集成
│   ├── ingest/            # 数据导入管道
│   ├── demo/              # Demo 服务器、智能体、数据库管理
│   ├── eval/              # Text2SQL 基准测试
│   ├── examples/          # 示例脚本
│   ├── servers/           # FastAPI / Flask / CLI 服务器
│   └── tools/             # 内置工具（run_sql, visualize_data, file_system）
├── frontends/webcomponent/# TypeScript Web 组件（Vite + Storybook）
├── tests/                 # Pytest 测试套件
├── n2s_app.py             # Demo 入口
├── pyproject.toml         # 项目元数据 + 依赖
├── docker-compose.yml     # Docker 部署
└── .env.example           # 环境变量模板
```

## 支持的 LLM 提供商

| 提供商 | 类型 | 需要 API Key | 说明 |
|--------|------|-------------|------|
| `mock` | 内置 | 否 | 确定性 Mock 响应，用于测试 |
| `openai` | 云端 | 是 | OpenAI GPT 模型 |
| `anthropic` | 云端 | 是 | Anthropic Claude 模型 |
| `gemini` | 云端 | 是 | Google Gemini 模型 |
| `ollama` | 本地 | 否 | 本地 Ollama 服务 |

## 支持的数据库

SQLite、PostgreSQL、MySQL、DuckDB、ClickHouse、Oracle、BigQuery、Snowflake、MS SQL Server、Hive、Presto（通过 SQLAlchemy 统一接入）。

## 致谢

N2S 基于 Vanna.AI 的 [Vanna](https://github.com/vanna-ai/vanna) 项目构建，遵循 MIT 许可证。

## 许可证

[MIT](./LICENSE)
