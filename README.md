# Enterprise Ops Agent

一个面向企业内部运营场景的 Agent 后端项目，基于 **FastAPI、LangGraph、PostgreSQL/pgvector 和 OpenAI-compatible LLM** 构建。

项目目标不是简单封装一个聊天接口，而是将企业 Agent 常见的工程能力串联起来：

- RAG 知识库问答
- LangGraph Agent 工作流编排
- 安全可控的工具调用
- SQL 白名单查询
- 工单 / 邮件草稿生成
- Human-in-the-loop 人工审批
- RAG / Agent 自动化评估
- Docker 化部署
- CI 单元测试验证

---

## 项目定位

Enterprise Ops Agent 模拟的是一个企业内部运营助手。

它可以处理以下几类任务：

```text
1. 查询企业知识库
2. 查询白名单范围内的业务数据
3. 生成工单草稿
4. 生成邮件草稿
5. 对写操作进行人工审批确认
```

典型场景：

```text
用户：报销政策里发票要求是什么？
Agent：走 RAG 检索知识库，返回答案和来源。

用户：帮我查一下 VIP 客户。
Agent：走预定义 SQL 白名单查询，只执行安全查询。

用户：帮我创建一个工单，反馈登录失败。
Agent：只生成工单草稿，进入 pending approval，不直接执行真实写操作。
```

---

## 核心能力

### 1. RAG 知识库问答

项目支持上传 `pdf`、`txt`、`md`、`markdown` 文档，并执行：

```text
文档解析 → 文本切分 → 本地 embedding → 写入 PostgreSQL/pgvector → 向量检索 → LLM 生成答案
```

RAG 查询结果会返回：

- `answer`：模型基于知识库生成的回答
- `sources`：命中的文档来源
- `debug`：检索数量、使用数量、最高分数等调试信息

相关模块：

```text
app/api/routes_documents.py
app/api/routes_rag.py
app/rag/chunking.py
app/rag/embeddings.py
app/rag/retriever.py
app/rag/generator.py
```

---

### 2. LangGraph Agent 编排

Agent 使用 LangGraph 编排执行流程：

```text
user_input
  ↓
router_node 判断 intent
  ↓
rag / sql / ticket / email / smalltalk
  ↓
final_node
```

当前支持的意图：

| Intent | 说明 |
|---|---|
| `rag_query` | 查询知识库 |
| `sql_query` | 查询业务数据 |
| `create_ticket` | 生成工单草稿 |
| `draft_email` | 生成邮件草稿 |
| `smalltalk` | 默认说明或兜底回答 |

相关模块：

```text
app/agent/graph.py
app/agent/nodes.py
app/agent/router.py
app/agent/tools.py
app/agent/memory.py
```

---

### 3. 安全工具调用

项目没有让 LLM 任意执行 SQL，也没有让 Agent 直接执行外部写操作。

SQL 查询采用白名单：

```text
list_vip_customers
list_pending_orders
```

写操作采用草稿 + 审批模式：

```text
生成工单草稿 / 邮件草稿
  ↓
approval_required = true
approval_status = pending
  ↓
用户调用 approve 接口确认或拒绝
```

当前版本即使审批通过，也只会把草稿标记为 `approved`，不会真实发送邮件或创建外部工单。

---

## 技术栈

| 方向 | 技术 |
|---|---|
| Web API | FastAPI, Uvicorn, Pydantic v2 |
| Agent | LangGraph |
| LLM | OpenAI-compatible API, Langfuse OpenAI wrapper |
| RAG | sentence-transformers, BAAI/bge-small-zh-v1.5 |
| Vector DB | PostgreSQL 16, pgvector |
| Database | SQLAlchemy 2.x, psycopg 3 |
| Test / CI | pytest, GitHub Actions |
| Deploy | Docker, Docker Compose |

---

## 架构简图

```text
Client
  ↓
FastAPI
  ├── Chat / Extract API
  ├── Documents API ── load/chunk/embed ── PostgreSQL + pgvector
  ├── RAG API ─────── retriever + generator ── LLM
  └── Agent API ───── LangGraph router/nodes/tools
                         ├── vector_search_tool
                         ├── sql_query_tool
                         ├── create_ticket_draft_tool
                         └── draft_email_tool
```

---

## 项目结构

```text
app/
  main.py                 FastAPI 入口
  config.py               环境变量配置
  api/                    API 路由
  agent/                  LangGraph Agent 编排、节点、工具、状态
  rag/                    文档加载、切分、embedding、检索、生成
  db/                     数据库连接、初始化、示例业务数据
  core/                   security、tracing、logging、metrics

evals/
  rag_questions.jsonl     RAG 评估集
  agent_tasks.jsonl       Agent 评估集
  run_rag_eval.py         RAG 评估脚本
  run_agent_eval.py       Agent 评估脚本

scripts/
  run_all_evals.py        汇总运行评估并生成报告

tests/                    pytest 测试
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
```

---

## 快速开始

### 1. 准备环境变量

复制环境变量文件：

```cmd
copy .env.example .env
```

根据实际环境填写 `.env`：

```env
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-5.5
OPENAI_API_BASE_URL=http://127.0.0.1:8080/v1
LLM_TIMEOUT_SECONDS=60

EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
EMBEDDING_DIM=512
EMBEDDING_DEVICE=cpu

DATABASE_URL=postgresql+psycopg://agent:agent@localhost:5432/agent_rag
UPLOAD_DIR=data/uploads
TOP_K=5
MIN_RAG_SCORE=0.45
MAX_INPUT_LENGTH=4000

NO_PROXY=localhost,127.0.0.1,::1,host.docker.internal
no_proxy=localhost,127.0.0.1,::1,host.docker.internal
```

如果本机开启了全局代理，建议保留 `NO_PROXY`，避免本地 API 或本地 LLM 请求被代理劫持。

---

### 2. 启动数据库

```cmd
docker compose up -d postgres
```

---

### 3. 安装依赖

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

### 4. 启动 API

```cmd
python app/main.py
```

默认地址：

```text
http://127.0.0.1:6002
```

健康检查：

```cmd
curl http://127.0.0.1:6002/health
```

接口文档：

```text
http://127.0.0.1:6002/docs
```

也可以使用 Docker 启动完整服务：

```cmd
docker compose up --build
```

Docker 方式下 API 地址：

```text
http://127.0.0.1:8000
```

---

## 评估方式

项目提供两类评估脚本。

### RAG Eval

```cmd
python -m evals.run_rag_eval
```

评估内容：

- 回答是否包含预期关键词
- source 是否命中预期文档
- 无资料问题是否正确拒答
- 平均延迟

---

### Agent Eval

```cmd
python -m evals.run_agent_eval
```

评估内容：

- intent 路由是否正确
- tool 调用是否正确
- approval_required 是否符合预期
- unsafe case 是否拒绝执行
- 平均延迟

---

### 汇总评估报告

```cmd
python -m scripts.run_all_evals
```

报告输出：

```text
evals/eval_report.md
```

说明：Eval 会真实依赖 LLM、embedding、数据库和已入库文档，不建议放进普通 CI 作为必跑任务。

---

## 测试与 CI

本地运行测试：

```cmd
pytest -q tests
```

CI 配置文件：

```text
.github/workflows/ci.yml
```

CI 当前主要验证：

- Python 依赖能安装
- PostgreSQL/pgvector service 能启动
- 单元测试能通过
- 路由、schema、工具、安全边界没有被破坏

普通 CI 不跑真实 LLM 和真实 embedding。真实效果通过本地 Eval 或后续手动 workflow 验证。

---

## 安全边界

### 输入安全

`app/core/security.py` 会拦截高风险输入，例如：

```text
删除所有、清空、drop table、truncate、绕过审批、直接发送、api key、secret key、数据库密码等
```

### 文件安全

只允许上传：

```text
pdf, txt, md, markdown
```

### SQL 安全

不允许 LLM 生成任意 SQL，只能执行预定义 `SAFE_SQL_MAP`。

### 写操作安全

邮件、工单等写操作只生成草稿，并进入 `pending approval`。当前版本不会真实发送邮件或创建外部工单。

### RAG 拒答

当检索不到超过 `MIN_RAG_SCORE` 的有效 chunk 时，系统返回：

```text
根据当前知识库资料，无法确认。
```

---

## 当前限制

- Agent memory 当前是简单 run 状态存储，不是生产级持久化会话记忆。
- 工单和邮件只生成草稿，没有接入真实外部系统。
- SQL 查询依赖白名单和规则匹配，不支持复杂 Text-to-SQL。
- RAG 文档管理能力较基础，暂缺文档删除、重建索引、版本管理。
- Agent Router 依赖 LLM structured output，需要模型服务兼容对应接口。
- CI 只验证离线单元测试，不验证真实 LLM 效果。
- Redis 在 docker-compose 中预留，但当前核心逻辑尚未强依赖 Redis。

---

## 后续优化方向

- 统一封装 LLM Client，集中处理 timeout、proxy bypass、错误日志和重试。
- 增加 retrieval-only eval，把 RAG 检索评估和 LLM 生成评估拆开。
- 增加 Agent Router fallback，当 LLM Router 不可用时走规则兜底。
- 将 Agent run、approval record、audit log 持久化到数据库。
- 增加用户体系、权限控制、API token、限流和审计日志。
- 增强 RAG 文档管理：列表、删除、重新索引、chunk 查看、按文档过滤。
- 增加 API smoke test、Docker build test、手动 eval workflow。

---

## 项目亮点

这个项目展示了一个企业 Agent 后端从原型到工程化的关键路径：

```text
FastAPI API
  + RAG 知识库
  + LangGraph Agent
  + 安全工具调用
  + Human Approval
  + Eval 评估
  + Docker 部署
  + CI 测试
```

它可以作为 AI Agent 后端工程化学习项目，也可以继续扩展成企业内部知识问答与运营自动化助手。
````