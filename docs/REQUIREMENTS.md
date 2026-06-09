# Resume Builder — 需求设计文档（v2）

日期：2026-06-09

---

## 一、产品定位

**AI 驱动的简历生成器。** 用户不需要知道怎么写简历，AI 通过问答引导用户，自动生成多份专业简历。

核心差异化：不是"给你一个模板自己填"，而是"告诉我你是谁，我帮你写"。

## 二、目标用户与痛点

| 用户 | 痛点 |
|------|------|
| 应届生 | 不知道怎么写第一份简历，不知道能投什么岗位 |
| 转行者 | 不知道如何把旧经验映射到新岗位 |
| 在校生 | 觉得没东西可写，不知道课程设计/社团经历也能写 |

## 三、核心流程

```
用户进入 → 输入背景（学校/专业/经历）
         ↓
       AI 分析 → 推荐岗位（前端/后端/算法/测试...）
         ↓
       用户勾选 → 前端 ✅ 后端 ✅  → 同时生成 2 份
         ↓
       进入问答式交互（逐个简历）
         ↓
       AI 自动补全 + 优化措辞
         ↓
       预览 + 导出 PDF
```

## 四、核心功能

### 4.1 智能岗位推荐（第一步）

用户输入基本信息：
```
我是 XX 大学 计算机科学专业 大四学生
会 Python 和 Java，做过一个课程设计（电商网站）
参加过 ACM 竞赛
```

AI 分析后推荐：
```
🟢 推荐岗位（勾选你想生成的）：
  ☑️ Java 后端开发（匹配度 92%）
  ☑️ Python 后端开发（匹配度 88%）
  ☐ 前端开发（匹配度 65%）
  ☐ 测试开发（匹配度 58%）
  ☐ 数据分析（匹配度 45%）
  ☐ 算法工程师（匹配度 30%，需要硕士）
```

用户可以多选，一次生成多份简历。

### 4.2 问答式简历生成（第二步）

选择了"Java 后端开发"后，AI 开始问答：

```
AI：我看到你做过电商网站项目，能说说你具体负责哪部分吗？
    比如：后端接口开发 / 数据库设计 / 前端页面 / 部署运维？

用户：我主要写了登录注册、商品列表和购物车功能，用的 Spring Boot + MySQL

AI：明白了！我再帮你补充一些细节——

    [AI 自动生成初稿]
    ● 基于 Spring Boot + MySQL 开发电商平台核心功能模块
    ● 实现用户认证（JWT + Spring Security），支持注册、登录、密码重置
    ● 设计 RESTful API，完成商品列表分页查询、购物车增删改查
    ● 使用 MyBatis 实现数据库交互，优化 SQL 查询性能

    这段话看起来可以吗？（你可以修改或确认继续）
    [确认] [修改]
```

### 4.3 AI 自动补全能力

| 用户说的 | AI 优化成 |
|---------|----------|
| "写过一些 Java 代码" | "熟练掌握 Java，具备面向对象编程和设计模式基础" |
| "负责数据库" | "使用 MySQL 进行数据库设计与优化，编写高效 SQL 查询" |
| "参加了社团" | "担任 XX 社团干事，组织策划 XX 人规模活动，锻炼了沟通协调能力" |
| "会用 Python" | "熟练使用 Python，掌握 Flask/Django Web 框架，具备数据处理和脚本编写能力" |

### 4.4 多简历并行生成

- 用户勾选 3 个岗位 → 生成 3 份独立简历
- 共享信息自动复用（个人信息、教育背景）
- 不同岗位有不同侧重点：
  - 后端岗：强调技术栈、系统设计
  - 前端岗：强调框架、项目经验
  - 算法岗：强调竞赛、论文、数学基础

## 五、页面结构

```
/                    首页 → 输入背景 → 获得岗位推荐
/recommend           岗位推荐页 → 勾选岗位 → 开始生成
/chat/:resumeId      问答页 → AI 对话式交互
/preview/:resumeId   预览页 → 查看/导出
```

## 六、AI 模块设计

| 模块 | 功能 | LLM |
|------|------|-----|
| 岗位分析 | 根据用户背景推荐合适岗位 | DeepSeek |
| 问答交互 | 多轮对话收集信息 | DeepSeek |
| 内容生成 | 将用户回答转为专业简历措辞 | DeepSeek |
| 模板匹配 | 根据岗位类型选择最佳模板 | 规则引擎 |

## 七、后端 API

```
POST  /api/analyze          # 提交背景 → 返回岗位推荐
POST  /api/resumes           # 创建简历（指定岗位）
GET   /api/resumes/:id       # 获取简历
POST  /api/resumes/:id/chat  # 发送对话消息 → AI 回复 + 更新简历
GET   /api/resumes/:id/export # 导出 PDF
```

## 八、数据库设计

```sql
CREATE TABLE resumes (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    title      VARCHAR(100) NOT NULL,
    role       VARCHAR(100) NOT NULL,       -- 目标岗位
    template   VARCHAR(50)  DEFAULT 'classic',
    data       JSON         NOT NULL,       -- 简历内容
    chat_history JSON       DEFAULT NULL,   -- 对话历史
    status     VARCHAR(20)  DEFAULT 'chatting', -- chatting/done/exported
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 九、技术栈调整

| 层面 | 原方案 | 新方案 |
|------|--------|--------|
| 核心驱动 | 模板 + 填表 | AI 对话 |
| 前端交互 | 表单 | 聊天界面 |
| 后端核心 | CRUD | LLM 调用编排 |
| LLM | 无 | DeepSeek API |
| Agent 框架 | 无 | AgentScope（复用 ezer-ai-assistant 配置） |

## 十、MVP 范围

**必做：**
- ✅ 背景输入 → AI 岗位推荐
- ✅ 多岗位勾选 → 并行生成多份简历
- ✅ 问答式交互（每份简历独立对话）
- ✅ AI 自动补全和措辞优化
- ✅ 基础模板渲染 + PDF 导出

**不做（二期）：**
- ❌ 用户登录系统
- ❌ 手动编辑模式
- ❌ 简历诊断/评分
- ❌ 校招/面经等生态
