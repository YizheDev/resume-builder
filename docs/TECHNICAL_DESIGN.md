# Resume Builder — 技术设计文档

日期：2026-06-09
版本：v1.0

---

## 一、技术架构

```
┌─────────────────────────────────────────────┐
│                  Nginx / Caddy                │
│              reverse proxy :80               │
├─────────────────────────────────────────────┤
│                                               │
│  ┌─────────────────────┐  ┌──────────────┐  │
│  │   Go Backend (:8081) │  │  MySQL (:3306) │  │
│  │                      │  │               │  │
│  │  /api/resumes        │  │  resumes 表    │  │
│  │  /api/templates      │  │               │  │
│  │  / (static files)    │  └──────────────┘  │
│  └─────────────────────┘                     │
│                                               │
│  内存占用: ~30MB Go + 已有 MySQL 共享         │
└─────────────────────────────────────────────┘
```

## 二、技术栈

| 层面 | 选型 | 版本 | 原因 |
|------|------|------|------|
| 后端 | Go | 1.21+ | 单二进制部署，30MB 内存 |
| Web 框架 | Gin | 1.9 | 最流行的 Go HTTP 框架 |
| ORM | GORM | 1.25 | Go 最成熟的 ORM |
| 前端 | Vue 3 + Vite | 3.4+ | 组件化，响应式 |
| 样式 | Tailwind CSS | 3.4 | 快速开发UI |
| PDF | html2pdf.js | 0.10 | 纯浏览器端生成 |
| 数据库 | MySQL | 8.4 | 复用已有实例 |
| 部署 | Docker | - | 单容器部署 |

## 三、项目结构

```
resume-builder/
├── AGENTS.md
├── AGENT_BOOTSTRAP_GUIDE.md
├── AGENT_DEVELOPMENT_GUIDE.md
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── docs/
│   ├── REQUIREMENTS.md
│   ├── TECHNICAL_DESIGN.md
│   └── ai/
│       └── (AI 协作模板)
├── server/
│   ├── main.go               # 入口
│   ├── go.mod / go.sum
│   ├── config/
│   │   └── config.go          # 配置管理
│   ├── handler/
│   │   ├── resume.go          # 简历 CRUD API
│   │   └── template.go        # 模板 API
│   ├── model/
│   │   └── resume.go          # 数据模型
│   ├── service/
│   │   └── resume.go          # 业务逻辑
│   └── middleware/
│       └── cors.go            # CORS 中间件
├── web/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── router/
│       │   └── index.js
│       ├── views/
│       │   ├── Home.vue       # 模板选择页
│       │   └── Editor.vue     # 编辑器页
│       ├── components/
│       │   ├── TemplateCard.vue
│       │   ├── ResumeForm.vue
│       │   ├── ResumePreview.vue
│       │   └── PdfExport.vue
│       └── templates/         # 简历模板 HTML/CSS
│           ├── classic.html
│           ├── professional.html
│           ├── tech.html
│           ├── minimal.html
│           └── english.html
└── templates/                 # Go 模板（可选，用于服务端渲染）
```

## 四、API 设计

```
GET    /api/resumes            # 简历列表
POST   /api/resumes            # 创建简历
GET    /api/resumes/:id        # 获取简历
PUT    /api/resumes/:id        # 更新简历
DELETE /api/resumes/:id        # 删除简历
GET    /api/templates          # 模板列表
```

### 请求/响应示例

```json
// POST /api/resumes
{
  "title": "我的简历",
  "template": "classic",
  "data": { "personal": {...}, "education": [...], ... }
}

// Response
{
  "code": 0,
  "message": "ok",
  "data": { "id": 1, "title": "我的简历", ... }
}
```

## 五、部署架构

```yaml
# docker-compose.yml
services:
  resume-builder:
    build: .
    ports:
      - "8081:8080"
    environment:
      - DB_HOST=host.docker.internal  # 使用宿主机 MySQL
      - DB_PORT=3306
      - DB_USER=root
      - DB_PASS=${DB_PASS}
      - DB_NAME=resume_builder
    restart: unless-stopped
```

## 六、前端路由

```
/                → Home.vue（模板选择）
/editor/:id      → Editor.vue（编辑器）
/editor/new      → Editor.vue（新建）
```

## 七、技术决策

| 决策 | 原因 |
|------|------|
| **Go 而非 Java** | 30MB vs 150MB 内存，包体积 15MB vs 40MB |
| **Vue 3 而非 React** | 你熟悉 Java，Vue 模板语法更接近后端思维 |
| **html2pdf 浏览器生成 PDF** | 零服务器 CPU 开销，PDF 文件不经过服务器 |
| **JSON 字段存储简历** | 灵活，模板变更不改变表结构 |
| **复用 MySQL** | 不再装新数据库，减少内存占用 |

## 八、安全考虑

- SQL 注入防护（GORM 参数化查询）
- XSS 防护（Vue 默认转义）
- 无用户认证，简历数据无所有权校验（个人使用，非公开服务）
- 环境变量注入数据库密码
