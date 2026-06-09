# Resume Builder — 技术设计文档（v4 最终版）

日期：2026-06-09

---

## 一、技术架构

```
┌──────────────────────────────────────────────────────────────────┐
│                         Nginx :80                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Python FastAPI (:8081)                         │  │
│  │                                                              │  │
│  │  ┌────────────────────────────────────────────────────┐    │  │
│  │  │        LangGraph Agent Pipeline                     │    │  │
│  │  │                                                    │    │  │
│  │  │  AnalyzeRole → CollectModules → GenerateContent    │    │  │
│  │  │       ↓              ↓               ↓             │    │  │
│  │  │  ReviewEnhance → ATSCheck → FormatOutput          │    │  │
│  │  └────────────────────────────────────────────────────┘    │  │
│  │                                                              │  │
│  │  ┌──────────────────────┐  ┌──────────────────────────┐   │  │
│  │  │  外部 MCP 服务        │  │  数据层                   │   │  │
│  │  │                      │  │                           │   │  │
│  │  │  CV Forge (PDF生成)   │  │  MySQL (简历存储)         │   │  │
│  │  │  Lightcast (技能库)   │  │  ChromaDB (向量检索)      │   │  │
│  │  │  ATS-Checker (评分)   │  └──────────────────────────┘   │  │
│  │  └──────────────────────┘                                   │  │
│  │                                                              │  │
│  │  LLM: DeepSeek API (中文生成)                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  内存: ~150MB Python + MCP 客户端 + ChromaDB                      │
└──────────────────────────────────────────────────────────────────┘
```

## 二、技术栈

| 层面 | 选型 | 原因 |
|------|------|------|
| 后端框架 | **FastAPI** | 异步，OpenAPI 自动生成 |
| AI 编排 | **LangGraph** | 多 Agent 流程，Reviewer→Enhancer |
| LLM 管理 | **AgentScope Python** | 统一多模型管理 + fallback |
| 向量检索 | **ChromaDB** | 轻量嵌入式，技能/岗位语义匹配 |
| 数据库 | MySQL 8.4 + SQLAlchemy | 复用已有 |
| PDF 生成 | **CV Forge MCP** (主) + WeasyPrint (兜底) | ATS 优化格式 |
| 技能数据 | **MCP Lightcast** | 48000+ 标准化技能库 |
| ATS 评分 | **ATS-Checker MCP** (CrewAI) | 多 Agent 评分 + 反馈 |
| 前端 | Vue 3 + Vite + Tailwind | 组件化 |
| 部署 | Docker 多阶段构建 | |

## 三、可复用资源整合

### 3.1 MCP 服务器（直接集成）

| MCP | 仓库 | 功能 | 集成方式 | 优先级 |
|-----|------|------|---------|--------|
| **CV Forge** | [thechandanbhagat/cv-forge](https://github.com/thechandanbhagat/cv-forge) | 解析 JD + ATS 优化 PDF 生成 | MCP Python SDK 调用 | 🔴 必装 |
| **Lightcast** | [lawwu/mcp-lightcast](https://github.com/lawwu/mcp-lightcast) | 48000 技能 + 73000 岗位 + 职业路径 | MCP HTTP 调用 | 🔴 必装 |
| **ATS-Checker** | [ATS-Checker-CrewAI](https://model-context-protocol.com/servers/ats-checker-resume-using-crewai-mcp) | 简历评分 + 优化建议 + PDF 报告 | MCP + CrewAI | 🟡 推荐 |
| **Resume Screening** | [run-llama/mcp_resume_screening](https://github.com/run-llama/mcp_resume_screening) | LlamaIndex 官方，JD 匹配 + 评分 | MCP Python SDK | 🟢 可选 |
| **Resume-MCP-Server** | [rajg1011/Resume-MCP-Server](https://github.com/rajg1011/Resume-MCP-Server) | 简历 Q&A + 面试准备 | MCP Node.js | 🟢 可选 |

### 3.2 Python 库（参考/复用源码）

| 项目 | 仓库 | 核心亮点 | 我们复用 |
|------|------|---------|---------|
| **ResumeCraftr** | [raestrada/ResumeCraftr](https://github.com/raestrada/ResumeCraftr) | LangGraph + ChromaDB，ATS 优化，无需 LaTeX | LangGraph Pipeline 架构 |
| **Tailor-My-Resume** | [ArpanSM/Tailor-My-Resume](https://github.com/ArpanSM/Tailor-My-Resume) | LangGraph + LiteLLM，多阶段 JD→LaTeX | 多阶段 Agent 流程 |
| **yaml-resume-builder** | [husayni/resume_builder](https://github.com/husayni/resume_builder) | YAML → LaTeX，自动一页优化 | 自动排版算法 |
| **ResuLLMe** | [skyiron/LLM-Resume](https://github.com/skyiron/LLM-Resume) | 现有 PDF→LLM增强→LaTeX | PDF 导入功能参考 |

### 3.3 参考项目（架构参考）

| 项目 | 仓库 | 亮点 | 参考点 |
|------|------|------|--------|
| **StackResume** | [Sathvik-Rao/StackResume](https://github.com/Sathvik-Rao/StackResume) | 多 Agent LangGraph，Reviewer→Enhancer，ATS 评分 | Agent Pipeline 设计 |
| **Reactive Resume** | [amruthpillai/reactive-resume](https://github.com/amruthpillai/reactive-resume) | 100 万用户，12 模板，自托管 | 前端模板交互 |
| **Mirror** | [prateekpuri01/mirror](https://github.com/prateekpuri01/mirror) | 双层级记忆，学习用户写作风格 | AI 记忆系统 |

## 四、前端架构与参考

### 4.1 前端技术栈

| 层面 | 选型 | 原因 |
|------|------|------|
| 框架 | Vue 3 (Composition API) | 组件化，响应式 |
| 状态管理 | Pinia | Vue 3 官方推荐 |
| UI 组件库 | **shadcn-vue** + Tailwind CSS | 现代、简洁、可定制 |
| 图标 | Lucide Vue | 轻量，现代风格 |
| PDF 预览 | html2pdf.js | 浏览器端渲染 A4 |
| 路由 | Vue Router 4 | SPA 路由 |
| 构建 | Vite 5 | 最快 |

### 4.2 前端参考项目

| 项目 | 仓库 | 亮点 | 我们参考 |
|------|------|------|---------|
| **V-Resume Builder** | [V381/V-Resume-Builder](https://github.com/V381/V-Resume-Builder) | Vue 3 + Pinia，A4 实时预览，PDF/DOC 导出 | A4 预览实现 |
| **Vue3 Awesome CV** | [derecklhw/replicate-awesome-cv-template](https://github.com/derecklhw/replicate-awesome-cv-template) | JSON 数据驱动的 A4 模板，组件化 | 模板数据结构 |
| **vue-resume-template** | [ryanbalieiro/vue-resume-template](https://github.com/ryanbalieiro/vue-resume-template) | 单页 A4 简历，~140 stars | 简洁排版参考 |
| **Reactive Resume** (React) | [amruthpillai/reactive-resume](https://github.com/amruthpillai/reactive-resume) | 100 万用户，12 模板，拖拽，AI 增强 | **UX 标杆**（架构参考） |

### 4.3 前端 UI 组件库对比

| 方案 | Stars | 特点 | 适合我们？ |
|------|-------|------|-----------|
| **shadcn-vue** | 15k+ | Tailwind 原生，组件可完全定制，暗色模式 | ⭐⭐⭐ 最推荐 |
| PrimeVue | 10k+ | 组件丰富，内置表单/图表/编辑器 | ⭐⭐ 组件多但重 |
| Nuxt UI | 10k+ | Nuxt 专用，Vue 3 原生 | ⭐ Nuxt 绑定 |
| Element Plus | 24k+ | 国内最流行，中文友好 | ⭐⭐ 老牌但风格偏传统 |

**选择 shadcn-vue + Tailwind**，因为：
- 组件简洁现代，适合聊天 + 表单场景
- 完全可定制，不会出现组件库风格限制
- 支持暗色模式（聊天界面暗色体验更好）
- 与 Tailwind 深度整合

### 4.4 核心页面组件树

```
App.vue
├── Home.vue                          # 首页
│   ├── HeroSection.vue               # 输入背景 + CTA
│   ├── QuickPreview.vue              # 30秒演示
│   └── TemplateShowcase.vue          # 模板展示
│
├── Recommend.vue                     # 岗位推荐
│   ├── BackgroundInput.vue           # 背景输入（复用）
│   ├── RoleCard.vue                  # 岗位卡片（匹配度 + 技能）
│   └── RoleSelectPanel.vue           # 多选面板
│
├── ChatView.vue                      # 对话式选择
│   ├── ChatMessage.vue               # 消息气泡（AI/用户）
│   ├── OptionSelector.vue            # 多选列表
│   ├── CustomInput.vue               # 自定义输入
│   ├── ProgressSidebar.vue           # 进度可视化
│   └── MiniPreview.vue               # 缩略预览
│
├── EditorView.vue                    # 编辑模式
│   ├── ModuleSidebar.vue             # 模块导航
│   ├── FormEditor.vue                # 表单编辑
│   ├── InlineA4Preview.vue           # A4 实时预览
│   ├── VersionTimeline.vue           # 版本历史
│   └── JDTargetPanel.vue             # JD 优化面板
│
└── ShareView.vue                     # 分享页
    ├── ResumeViewer.vue              # 只读预览
    └── CommentSection.vue            # 评论
```

### 4.5 A4 预览实现方案

参考 V-Resume Builder 的实现：
```vue
<!-- InlineA4Preview.vue -->
<template>
  <div class="a4-container">
    <div class="a4-page" :style="{ width: '210mm', minHeight: '297mm' }">
      <!-- 缩放容器 -->
      <div class="scale-wrapper" :style="{ transform: `scale(${scale})` }">
        <component :is="templateComponent" :data="resumeData" />
      </div>
    </div>
  </div>
</template>

<style>
.a4-page {
  background: white;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  margin: 0 auto;
  padding: 20mm;
}
.scale-wrapper {
  transform-origin: top left;
  width: 170mm; /* 210mm - 2*20mm padding */
}
</style>
```

### 4.6 对话界面设计

参考现代聊天应用（ChatGPT/Claude 风格）：
- 左侧对话区 60% + 右侧 A4 缩略预览 40%
- AI 消息：白色气泡 + 左侧对齐
- 选项列表：卡片式多选，带推荐标签
- 用户消息：蓝色气泡 + 右侧对齐
- 进度条：顶部固定
- 输入框：底部固定，支持快捷键（Enter 发送）

```vue
<!-- ChatView.vue 布局 -->
<div class="flex h-screen">
  <div class="w-3/5 flex flex-col">
    <ProgressSidebar />
    <div class="flex-1 overflow-y-auto p-6">
      <ChatMessage v-for="msg in messages" :key="msg.id" />
    </div>
    <div class="p-4 border-t">
      <ChatInput @send="handleSend" />
    </div>
  </div>
  <div class="w-2/5 bg-gray-100 p-4 overflow-y-auto">
    <MiniPreview :data="resumeData" />
  </div>
</div>
```

## 五、LangGraph Agent Pipeline

### 4.1 完整流程

```python
from langgraph.graph import StateGraph

workflow = StateGraph(ResumeState)

# 步骤 1：岗位分析
workflow.add_node("analyze_role", analyze_role)
# 输入: 用户背景  → 输出: 岗位推荐列表
# 数据: DeepSeek API + Lightcast 技能库验证

# 步骤 2：逐模块收集信息
workflow.add_node("collect_modules", collect_modules)
# 对每个模块(7个):
#   AI 生成高质量选项列表
#   用户勾选 + 自定义输入
#   智能推荐关联选项

# 步骤 3：生成简历内容
workflow.add_node("generate_content", generate_content)
# 汇总所有选择 + 自定义输入
# DeepSeek 生成完整 JSON 简历
# 参考 ResumeCraftr 的 Prompt 结构

# 步骤 4：AI 审查优化
workflow.add_node("review_enhance", review_enhance)
# 参考 StackResume 的 Reviewer→Enhancer
# 检查: 内容完整性 / 措辞专业性 / 量化数据 / 模块衔接

# 步骤 5：ATS 兼容性检查
workflow.add_node("ats_check", ats_check)
# 调用 ATS-Checker MCP (CrewAI)
# 检查: 关键词覆盖 / 格式兼容 / 评分 + 建议

# 步骤 6：格式化输出
workflow.add_node("format_output", format_output)
# 调用 CV Forge MCP 生成 PDF
# 失败则 WeasyPrint 兜底

# 流程连接
workflow.set_entry_point("analyze_role")
workflow.add_edge("analyze_role", "collect_modules")
workflow.add_edge("collect_modules", "generate_content")
workflow.add_edge("generate_content", "review_enhance")
workflow.add_edge("review_enhance", "ats_check")
workflow.add_edge("ats_check", "format_output")
```

### 4.2 LLM 调用策略

```
岗位分析   → DeepSeek (中文理解好)
内容生成   → DeepSeek (中文生成好)
内容润色   → DeepSeek (STAR法则 + 量化)
ATS 检查   → DeepSeek + ATS-Checker MCP
技能匹配   → Lightcast MCP (标准化技能库)
PDF 生成   → CV Forge MCP (ATS 优化格式)
```

## 五、MCP SDK 集成代码

### 5.1 CV Forge — PDF 生成

```python
# server/services/pdf_exporter.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def generate_pdf_with_cvforge(resume_data: dict, template: str = "professional") -> bytes:
    """通过 CV Forge MCP 生成 ATS 优化的 PDF"""
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@anthropic/cv-forge-mcp-server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("generate_cv", {
                "data": resume_data,
                "template": template,
                "format": "pdf",
            })
            return result.content[0].data  # PDF bytes
```

### 5.2 Lightcast — 技能库查询

```python
# server/services/skill_service.py
import httpx

class LightcastSkillService:
    """通过 Lightcast MCP 获取标准化技能数据"""

    BASE_URL = "https://mcp.lightcast.io/api"

    async def search_skills(self, keyword: str, limit: int = 20) -> list[dict]:
        """搜索相关技能"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/skills/search",
                params={"q": keyword, "limit": limit},
            )
            return resp.json()["data"]

    async def get_role_skills(self, role: str) -> list[dict]:
        """获取某岗位的常见技能"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/occupations/skills",
                params={"title": role},
            )
            return resp.json()["data"]
```

### 5.3 ATS-Checker — 简历评分

```python
# server/services/ats_checker.py
async def check_resume_ats(resume_data: dict) -> dict:
    """调用 ATS-Checker MCP 评分 + 获取优化建议"""
    # CrewAI 多 Agent: Parser → Analyzer → Scorer → Reporter
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "ats_checker_mcp"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            result = await session.call_tool("analyze_resume", {
                "resume": resume_data,
            })
            return {
                "score": result.content[0].json["score"],
                "feedback": result.content[0].json["feedback"],
                "suggestions": result.content[0].json["suggestions"],
            }
```

## 六、API 设计（不变）

```
POST  /api/analyze           # 背景分析 → 岗位推荐（含 Lightcast 数据）
POST  /api/resumes            # 创建简历
GET   /api/resumes/:id        # 获取简历
POST  /api/resumes/:id/chat   # LangGraph Agent 对话
POST  /api/resumes/:id/generate  # 触发完整 Pipeline
GET   /api/resumes/:id/export    # PDF 导出（CV Forge MCP）
GET   /api/skills/search?q=   # 技能搜索（Lightcast MCP）
POST  /api/resumes/:id/ats-check  # ATS 评分（ATS-Checker MCP）
```

## 七、项目结构

```
resume-builder/
├── server/
│   ├── main.py                    # FastAPI 入口
│   ├── config.py                  # 配置管理
│   ├── database.py                # SQLAlchemy
│   ├── models/
│   │   └── resume.py              # ORM 模型
│   ├── routers/
│   │   ├── analyze.py             # 岗位分析
│   │   ├── resumes.py             # 简历 CRUD
│   │   ├── chat.py                # Agent 对话
│   │   ├── export.py              # PDF 导出
│   │   └── skills.py              # 技能搜索
│   ├── services/
│   │   ├── llm_service.py         # DeepSeek 调用
│   │   ├── pdf_exporter.py        # CV Forge MCP + WeasyPrint
│   │   ├── skill_service.py       # Lightcast MCP
│   │   ├── ats_checker.py         # ATS-Checker MCP
│   │   └── mcp_manager.py         # MCP 连接管理
│   └── agents/
│       ├── pipeline.py            # LangGraph 主流程
│       ├── analyze_agent.py       # 岗位分析 Agent
│       ├── collect_agent.py       # 模块收集 Agent
│       ├── generate_agent.py      # 内容生成 Agent
│       ├── review_agent.py        # 审查优化 Agent
│       └── ats_agent.py           # ATS 检查 Agent
├── web/                           # Vue 3 前端（不变）
├── requirements.txt
├── Dockerfile
└── docs/
    ├── REQUIREMENTS.md
    └── TECHNICAL_DESIGN.md
```

## 八、部署

```
47.113.110.222
  ├── :8080  ezer-ai-assistant (Java, 日报)
  ├── :8081  resume-builder (Python, 简历)
  └── :3306  MySQL (共享)
```

## 九、开发路线图

| 阶段 | 内容 | 预计时间 |
|------|------|---------|
| 1 | FastAPI 骨架 + 数据库 + CRUD API | 2h |
| 2 | DeepSeek LLM 集成 + 岗位分析 | 2h |
| 3 | LangGraph Agent Pipeline | 3h |
| 4 | CV Forge MCP 集成 (PDF) | 1h |
| 5 | Lightcast MCP 集成 (技能库) | 1h |
| 6 | ATS-Checker MCP (评分) | 1h |
| 7 | Vue 前端（选择式交互） | 4h |
| 8 | 部署 + 测试 | 1h |
| **合计** | | **~2 天** |
