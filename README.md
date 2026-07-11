# Agent Dev Week 1 （version：V1）


这是一个用与学习 AI agent 后端基础能力的第一周练习项目。

当前项目基于 FastAPI 构建，主要包含： 

- FastAPI 后端服务
- LLM 普通对话接口
- LLM 流式输出接口
- Structured Output 结构化输出接口
- 本地工具函数
- pytest 基础测试


> 注意：当前版本是第一周学习版本，重点是理解 LLM 后端基础工程结构，还不是完整的 Agent 框架项目。
---------

## 项目结构

```text
agent-dev-week1/
    app/
        __init__.py
        main.py
        config.py
        schemas.py
        llm.py
        tools.py
        api/
            __init__.py
            routes_chat.py
            routes_extract.py
            routes_tools.py
    tests/
        test_health.py
        test_schemas.py
        test_tools.py
    .env.example
    requirements.txt
    README.md
```

## 目录说明
```text
app/main.py
```
FastAPI应用入口，负责创建app、注册路由、定义健康检查接口和异常处理。

```text
app/config.py
```
负责读取环境变量，例如OpenAI API Key、模型名称、API Base URL。

```text
app/schemas.py
```
定义请求和响应的数据结构，例如聊天消息、聊天请求、结构化任务提取结果

```text
app/llm.py
```
封装LLM调用逻辑，包括普通聊天、结构化输出、工具schema和本地工具执行函数

```text
app/tools.py
```
定义本地工具函数，目前包括：
- `calculator(expression)`：安全计算简单数学表达式
- `get_current_time()`：获取当前服务器时间

```text
app/api/routes_chat.py
```

定义聊天相关接口：
- `/api/chat`
- `/api/chat/stream`

```text
app/api/routes-extract.py
```

定义结构化任务提取接口
- `/api/extrac-task`

```text
app/api/routes-tools.py
```
定义工具聊天接口文件。
当前main.py已经注册该路由，
所以`/api/tool-chat`当前暂时不可用。

```text
tests/
```
存放pytest测试代码。

## 环境准备

### 1. 创建虚拟环境

```
python -m venv .venv
```

### 2. 激活虚拟环境
Windows cmd
`.venv\Scripts\activate`

macos/Linux:
`source .venv/bin/activate`

### 3. 安装依赖
`pip install -r requirements.txt`

## 环境变量配置
项目需要`.env`文件保存模型配置
可以先复制实例文件：
window cmd：
`copy .env.example .env`

macOS/Linux:
`cp .env.examlpe .env`

`.env.example`实例：
```
OPENAI_API_BASE_URL=yourbase_url_here
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.5
```
你需要在`.env`中填写真实配置

## 启动项目
当前 `app/mian.py`中设置的端口是`6002`
可以直接运行
`python app/main.py`

也可以使用uvicorn启动:
`uvicorn app.main:app --reload --port 6002`

启动后访问接口文档
`http://127.0.0.1:6002/docs`

健康检查
`http://127.0.0.1:6002/health`

## 当前可用接口

1.健康检查

`GET /health`

实例请求
`curl http"//127.0.0.1:6002/health`

返回示例:
```
{
    "status":"ok"
}
```

2.普通聊天接口

`POST /api/chat`

请求示例:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "用一句话解释什么是 AI Agent"
    }
  ],
  "temperature": 0.2
}
```

windows cmd curl 示例:

```
curl -X POST "http://127.0.0.1:6002/api/chat" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"用一句话解释什么是 AI Agent\"}],\"temperature\":0.2}"
```

返回示例:
```json
{
  "answer": "AI Agent 是能够理解目标、调用工具并完成任务的智能程序。"
}

```

3.流式聊天接口

`POST /api/chat_stream`

当前版本使用的是伪流式输出
```python
for char in text:
    yield char
```
也就是说,接口会先拿到完整的模型回答,然后按字符逐步返回.

请求示例:
```cmd
curl -X POST "http://127.0.0.1:6002/api/chat_stream" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"介绍一下 AI\"}],\"temperature\":0.2}"
```

4.结构化任务提接口

`POST /api/extract_task`

该接口用于让模型按照固定结构返回`JSON`.

示例:
```json
{
    "text": "帮我给财务写一封邮件，说明这张发票需要重新审核，比较紧急。"
}
```

windows cmd curl 示例:
```cmd
curl -X POST "http://127.0.0.1:6002/api/extract_task" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"text\":\"帮我给财务写一封邮件，说明这张发票需要重新审核，比较紧急。\"}"
```

返回示例:
```json
{
  "intent": "email",
  "summary": "给财务写邮件说明发票需要重新审核",
  "priority": "high",
  "needs_tool": true
}
```

字段说明:

```
intent      任务类型，可选 question / todo / email / bug_report / unknown
summary     任务摘要
priority    优先级，可选 low / medium / high
needs_tool  是否需要调用工具
```

## 当前不可用接口
项目中虽然存在:

`app/api/routes_tools.py`

里面定义了:

`POST /api/tool-chat`

当前`app/main.py`注册了:
```python
from app.api.routes_tools import router as tools_router
app.include_router(tools_router)
```
不过当前版本的 Tool Chat 仍然是占位实现，内部暂时复用普通聊天逻辑。
本阶段重点是完成工具函数、工具 schema、安全边界和路由注册。
完整 Tool Calling Loop 会在后续版本实现。


## 本地工具函数
当前项目实现了两个本地工具.

### calculator

文件位置:

`app/tools.py`

功能:计算简单数学表达式

示例:
```python
calculator("2 + 3")
# 结果：5
```
该工具没有使用 Python 内置的 `eval()`，而是使用 `ast.parse()` 做受限表达式解析。

这样做的原因是：
```text
eval() 可以执行任意 Python 代码，存在安全风险。
ast.parse() 可以限制只支持数字和指定运算符，更适合工具调用场景。
```

### get_current_time

功能：获取当前服务器时间。

示例：
```
get_current_time()
# 返回：2026-07-09T17:30:00
```
## 运行测试

推荐使用：

`python -m pytest -q`

当前测试包括：
```
tests/test_health.py    测试 /health 接口
tests/test_schemas.py   测试 Pydantic 数据模型
tests/test_tools.py     测试本地工具函数
```

## 当前项目已完成功能
```
1. FastAPI 后端服务
2. /health 健康检查接口
3. 普通 LLM 聊天接口 /chat
4. 伪流式聊天接口 /chat_stream
5. 结构化输出接口 /extract_task
6. 本地工具 calculator
7. 本地工具 get_current_time
8. pytest 基础测试
```

## 当前项目待优化点

当前版本还不是最终工程化版本，后续可以继续优化：

```text
1. 统一 API 前缀为 /api
2. 将 /chat_stream 改为 /api/chat/stream
3. 将 /extract_task 改为 /api/extract-task
4. 注册 routes_tools.py，让 /api/tool-chat 可用
5. config.py 改成 Pydantic v2 推荐写法
6. 新增接口路径测试
7. 补充真正的 LLM streaming
8. 后续实现完整 Tool Calling Loop
```

---

## 学习重点

通过这个项目，需要理解：

```text
1. FastAPI 如何组织后端接口
2. Pydantic 如何校验请求体
3. .env 如何管理敏感配置
4. LLM API 如何封装到单独模块
5. Structured Output 为什么适合 Agent 路由判断
6. Tool Calling 为什么需要安全边界
7. pytest 如何测试接口、schema 和工具函数
8. README 为什么也是项目交付的一部分
```


<!-- docs: verify github contribution email -->

_Last updated: 2026-07-11_
