# Resume Builder — 技术设计文档（v2）

日期：2026-06-09

---

## 一、技术架构

```
┌─────────────────────────────────────────────────────┐
│                   Nginx :80                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────┐  ┌─────────────────┐ │
│  │  Go Backend (:8081)       │  │  MySQL (:3306)   │ │
│  │                           │  │                  │ │
│  │  /api/analyze  ←───┐     │  │  resumes 表       │ │
│  │  /api/resumes        │     │  │                  │ │
│  │  /api/resumes/:id/chat │   │  └─────────────────┘ │
│  │                      │     │                      │
│  │  LLMService ─────────┘     │                      │
│  │     │                      │                      │
│  │     ├── 岗位分析            │                      │
│  │     ├── 对话管理            │                      │
│  │     └── 内容生成            │                      │
│  │     ↓                      │                      │
│  │  DeepSeek API               │                      │
│  └──────────────────────────┘                       │
│                                                      │
│  内存: ~40MB Go + LLM 调用（外部）                    │
└─────────────────────────────────────────────────────┘
```

## 二、技术栈

| 层面 | 选型 | 原因 |
|------|------|------|
| 后端 | Go 1.21 + Gin | 轻量，省内存 |
| LLM | DeepSeek API | 中文好，便宜 |
| 数据库 | MySQL 8.4 | 复用已有 |
| 前端 | Vue 3 + Vite | 组件化 |
| 样式 | Tailwind CSS | 快速开发 |
| PDF | html2pdf.js | 浏览器端生成 |
| Agent 框架 | AgentScope | 可选——复用 ezer-ai-assistant 的模型配置 |

## 三、核心模块

### 3.1 LLMService

```
LLMService
  ├── analyzeCareer(userBackground) → []JobRecommendation
  │     输入：用户背景文本
  │     输出：推荐岗位列表（名称 + 匹配度 + 理由）
  │
  ├── chat(resumeId, userMessage, chatHistory) → AIResponse
  │     输入：用户消息 + 历史对话 + 已收集的信息
  │     输出：AI 回复（追问或确认）+ 更新的简历字段
  │
  └── polish(rawText, role) → PolishedText
        输入：用户的原始描述 + 目标岗位
        输出：优化后的专业措辞
```

### 3.2 Prompt 设计要点

**岗位分析 Prompt：**
```
你是职业规划专家。根据以下用户背景，推荐 5 个最适合的岗位。
对每个岗位给出：名称、匹配度(0-100)、推荐理由(一句话)、所需技能。
输出 JSON 格式。

用户背景：{input}
```

**对话式生成 Prompt：**
```
你正在帮助用户创建一份 {岗位} 的简历。
已收集信息：{collected}
对话历史：{history}

根据用户最新回复，提取有效信息更新简历字段。
如果有信息缺失，继续追问。用友好鼓励的语气。
输出 JSON：{ reply, fields_updated: {...}, next_question }
```

## 四、API 设计

```
POST /api/analyze
  请求: { "background": "我是XX大学计算机专业..." }
  响应: { "recommendations": [
    { "role": "Java后端开发", "score": 92, "reason": "...", "skills": ["Spring","MySQL"] }
  ]}

POST /api/resumes
  请求: { "role": "Java后端开发" }
  响应: { "id": 1, "status": "chatting" }

POST /api/resumes/:id/chat
  请求: { "message": "我主要写后端接口" }
  响应: {
    "reply": "明白了！我还想问...",
    "fields": { "experience[0].description": "...", "skills": ["Java","Spring"] },
    "status": "chatting"  // chatting | ready
  }

GET /api/resumes/:id
  响应: { "id": 1, "data": {...}, "status": "ready" }

GET /api/resumes/:id/export?format=pdf
  响应: PDF 文件流
```

## 五、数据库

```sql
CREATE TABLE resumes (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(100) NOT NULL DEFAULT '未命名简历',
    role         VARCHAR(100) NOT NULL,
    template     VARCHAR(50)  DEFAULT 'classic',
    data         JSON         NOT NULL,
    chat_history JSON,           -- [{role,content},...]
    status       VARCHAR(20)  DEFAULT 'chatting',
    created_at   DATETIME    DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 六、前端页面

```
/                     首页 — 输入背景
/recommend            推荐页 — 展示岗位列表 + 勾选
/chat/:id             对话页 — 聊天界面 + 简历预览
/preview/:id          预览页 — A4 预览 + 导出
```

### 对话页布局

```
┌──────────────────────────────────────────────┐
│  左侧：对话区（60%）                          │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │ AI: 你好！我是你的简历助手。             │ │
│  │ 看到你有电商项目经验，能具体说说吗？       │ │
│  └─────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────┐ │
│  │ 用户: 我写了登录注册、商品列表、购物车    │ │
│  └─────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────┐ │
│  │ AI: 很棒！我帮你整理成了专业描述：        │ │
│  │ ✨ [生成的简历内容预览]                   │ │
│  │ [确认] [修改]                             │ │
│  └─────────────────────────────────────────┘ │
│                                               │
│  [输入框] [发送]                              │
├──────────────────────────────────────────────┤
│  右侧：简历实时预览（40% 缩略）               │
│  ┌──────────────────────┐                    │
│  │  📄 A4 纸预览          │                    │
│  │  实时更新              │                    │
│  └──────────────────────┘                    │
│  [导出 PDF]                                  │
└──────────────────────────────────────────────┘
```

## 七、部署

与 ezer-ai-assistant 共用服务器：

```
47.113.110.222
  ├── :8080  ezer-ai-assistant (日报推送)
  ├── :8081  resume-builder  (简历生成)
  └── :3306  MySQL (共享)
```

```bash
# 环境变量
DB_USER=root
DB_PASS=xxx
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=resume_builder
DEEPSEEK_API_KEY=sk-xxx    # 复用 ezer-ai-assistant 的 key
```
