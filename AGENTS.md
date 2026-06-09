# AGENTS.md — Resume Builder AI 开发强制规则

## 0. 项目身份

- 项目名称：Resume Builder（AI 简历生成器）
- 项目描述：AI 驱动的简历生成工具，通过问答式交互自动生成多份专业简历
- 技术栈：Python 3.12 + FastAPI + Vue 3 + Vite + MySQL 8.4 + DeepSeek API
- AI 框架：LangGraph + AgentScope Python
- PDF 引擎：resumake-mcp（LaTeX）+ WeasyPrint 兜底
- 当前阶段：需求设计阶段（未开始编码）
- 部署位置：Docker 容器，与 ezer-ai-assistant 同服务器(47.113.110.222)
- 访问地址：http://47.113.110.222:8081

## 1. AI 工作前必须阅读

| 优先级 | 文档 | 说明 |
|--------|------|------|
| 1 | `docs/REQUIREMENTS.md` | 需求设计文档，每次必读 |
| 2 | `docs/TECHNICAL_DESIGN.md` | 技术设计文档，每次必读 |
| 3 | `AGENT_DEVELOPMENT_GUIDE.md` | Agent 开发全流程规范 |
| 4 | `AGENT_BOOTSTRAP_GUIDE.md` | 项目冷启动指南 |

## 2. 编码规范优先级

1. Go 官方 [Effective Go](https://go.dev/doc/effective_go)
2. Vue 3 [风格指南](https://vuejs.org/style-guide/)
3. 多个任务输入或规则冲突时，先停下来向人类确认

## 3. AI 开发硬性限制

- 不得引入新框架、新中间件、新外部服务，除非先新增决策记录并得到人工确认
- 不得把密钥、Token、API Key 写入代码、配置文件
- 不得在业务日志中打印敏感信息
- 不得吞掉异常。Go 中 error 必须处理或向上传递
- 所有密钥通过环境变量注入
- 前端不硬编码后端地址，通过 vite config 代理

## 4. 技术选型原则

- 优先轻量、单二进制部署
- Go 后端编译为一个可执行文件
- Vue 前端编译为静态文件，由 Go 服务托管
- 复用服务器已有 MySQL，不新建数据库实例
- 新增依赖前评估必要性，避免 vendor 膨胀

## 5. 项目结构约定

- `server/`  Go 后端代码
- `web/`    Vue 3 前端代码
- `docs/`   设计文档
- 前端构建产物输出到 `server/static/`，Go embed 打包进二进制
