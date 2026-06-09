# Resume Builder — 技术设计文档（v3 Python 版）

日期：2026-06-09

---

## 一、技术架构

```
┌──────────────────────────────────────────────────────────────┐
│                      Nginx :80                                │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────┐  ┌──────────────────┐   │
│  │  Python FastAPI (:8081)         │  │  MySQL (:3306)    │   │
│  │                                 │  │                   │   │
│  │  /api/analyze    岗位分析       │  │  resumes 表       │   │
│  │  /api/resumes    CRUD           │  └──────────────────┘   │
│  │  /api/resumes/:id/chat  对话    │                          │
│  │  /api/resumes/:id/export PDF   │                          │
│  │                                 │                          │
│  │  ┌──────────────────────────┐  │                          │
│  │  │  LangGraph Agent Pipeline │  │                          │
│  │  │                          │  │                          │
│  │  │  AnalyzeRole → AskModules│  │                          │
│  │  │  → GenerateContent        │  │                          │
│  │  │  → ReviewEnhance → Output│  │                          │
│  │  └──────────────────────────┘  │                          │
│  │           ↓                     │                          │
│  │  DeepSeek API + resumake-mcp    │                          │
│  └────────────────────────────────┘                          │
│                                                               │
│  内存: ~150MB Python + 已有 MySQL                              │
└──────────────────────────────────────────────────────────────┘
```

## 二、技术栈

| 层面 | 选型 | 原因 |
|------|------|------|
| 后端框架 | **FastAPI** | 异步支持，OpenAPI 自动生成，Python 生态 |
| LLM 编排 | **LangGraph** | 多 Agent 流程编排，Reviewer→Enhancer 天然支持 |
| LLM 调用 | **AgentScope Python** | 统一管理 DeepSeek + 多模型 fallback |
| PDF 生成 | **resumake-mcp** + WeasyPrint 兜底 | LaTeX 质量 PDF + 中文支持 |
| 数据库 | MySQL 8.4 (SQLAlchemy) | 复用已有 |
| 前端 | Vue 3 + Vite | 组件化，响应式 |
| 样式 | Tailwind CSS | 快速开发 |
| 部署 | Docker | 多阶段构建 |

## 三、MCP 集成

### 3.1 resumake-mcp

```python
# 集成方式：通过 MCP Python SDK 调用
from mcp import ClientSession

async def generate_pdf(resume_data: dict) -> bytes:
    """调用 resumake-mcp 生成 LaTeX 质量 PDF"""
    async with ClientSession(...) as session:
        result = await session.call_tool("generate_resume", resume_data)
        return result.content[0].data  # PDF bytes
```

优势：
- 9 套 LaTeX 模板，排版质量远超 HTML 转 PDF
- 支持自然语言描述生成
- 路径安全，文件夹管理

### 3.2 LangGraph Agent Pipeline

```python
from langgraph.graph import StateGraph

# 参考 StackResume 的 Reviewer→Enhancer 流程
workflow = StateGraph(ResumeState)
workflow.add_node("analyze_role", analyze_role)       # 岗位分析
workflow.add_node("ask_modules", ask_modules)         # 逐模块选择
workflow.add_node("generate_content", generate)        # 内容生成
workflow.add_node("review_enhance", review_enhance)   # AI 审查优化
workflow.add_node("format_output", format_output)     # 格式化输出

workflow.add_edge("analyze_role", "ask_modules")
workflow.add_edge("ask_modules", "generate_content")
workflow.add_edge("generate_content", "review_enhance")
workflow.add_edge("review_enhance", "format_output")
```

### 3.3 AgentScope 模型管理

```python
import agentscope

# 复用 ezer-ai-assistant 的模型配置模式
models = {
    "deepseek": agentscope.OpenAIChatModel(
        model_name="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1",
    ),
    "qwen": agentscope.DashScopeChatModel(...),  # 备用
}
```

## 四、项目结构

```
resume-builder/
├── AGENTS.md
├── AGENT_BOOTSTRAP_GUIDE.md
├── AGENT_DEVELOPMENT_GUIDE.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Makefile
├── docs/
│   ├── REQUIREMENTS.md
│   └── TECHNICAL_DESIGN.md
├── server/
│   ├── main.py                  # FastAPI 入口
│   ├── config.py                # 配置管理
│   ├── database.py              # SQLAlchemy 模型
│   ├── models/
│   │   └── resume.py            # Resume ORM 模型
│   ├── routers/
│   │   ├── analyze.py           # 岗位分析 API
│   │   ├── resumes.py           # 简历 CRUD API
│   │   └── chat.py              # 对话 API
│   ├── services/
│   │   ├── llm_service.py       # LLM 调用封装
│   │   ├── career_advisor.py    # 岗位推荐
│   │   ├── resume_generator.py  # 简历生成 Agent
│   │   ├── content_polisher.py  # 内容润色
│   │   └── pdf_exporter.py      # PDF 导出（MCP）
│   └── agents/
│       ├── analyze_agent.py     # 岗位分析 Agent
│       ├── module_agent.py      # 模块选择 Agent
│       ├── generate_agent.py    # 内容生成 Agent
│       └── review_agent.py      # 审查优化 Agent
├── web/                         # Vue 3 前端（不变）
│   └── ...
└── templates/
    └── resume_templates/        # 简历模板定义
```

## 五、API 设计

```
POST /api/analyze
  请求: { "background": "我是XX大学计算机专业..." }
  响应: {
    "recommendations": [
      { "role": "Java后端开发", "score": 92, "reason": "...", "skills": [...] }
    ]
  }

POST /api/resumes
  请求: { "role": "Java后端开发" }
  响应: { "id": 1, "status": "chatting" }

POST /api/resumes/:id/chat
  请求: { "message": "我勾选了API开发" }
  响应: {
    "reply": "好的，我还想了解...",
    "module": "experience",
    "options": [...],              # 下一轮选项
    "updated_fields": {...}
  }

POST /api/resumes/:id/generate
  请求: {}  # 全部模块收集完毕，一键生成
  响应: { "status": "generating" }

GET /api/resumes/:id/export?format=pdf
  响应: PDF 文件流（通过 resumake-mcp 生成）
```

## 六、部署

与 ezer-ai-assistant 共用服务器：

```
47.113.110.222
  ├── :8080  ezer-ai-assistant (Java, 日报)
  ├── :8081  resume-builder (Python, 简历)
  └── :3306  MySQL (共享)
```

```bash
# 环境变量
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASS=xxx
DB_NAME=resume_builder
DEEPSEEK_API_KEY=sk-xxx
```

## 七、对比总结

| | Go 方案 | Python 方案 |
|------|------|------|
| 内存 | 30MB | 150MB |
| 开发周期 | 3-4 天 | 2-3 天 |
| MCP 集成 | 手写 | 原生 SDK |
| Agent 框架 | 无 | LangGraph + AgentScope |
| PDF 质量 | HTML 转 PDF | LaTeX（resumake-mcp） |
| 中文支持 | 一般 | 丰富 |
| 参考项目 | 0 | 3+ |
