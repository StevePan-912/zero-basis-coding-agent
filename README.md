# ZerGO Coding Agent

ZerGO Coding Agent - 双模式智能编程学习和开发系统，帮助完全零基础的初学者学习编程概念并完成实际代码开发任务。

## 项目简介

### 核心定位

ZerGO Coding Agent 是帮助完全零基础的初学者学习编程概念并完成实际代码开发任务的双模式智能Agent系统。

### 品牌理念

**ZerGO** = **Zero** + **GO**，寓意"从零基础出发，即刻开始编程之旅"

### 目标用户

完全零基础的初学者（从未写过代码，需要从最基础概念开始学习）。

### 主要用途

两者兼顾 - 学习编程概念和完成实际开发任务。

## 功能特性

### 双模式系统

- **教学模式**: 详细解释概念、代码逐行解释、学习路径推荐
- **实用模式**: 快速生成代码、简化解释、一键部署运行
- **灵活切换**: 用户可手动切换模式，根据需求灵活使用

### 智能难度适配

- **零基础**: 使用类比、避免技术术语、提供基础概念链接
- **初级**: 适度技术术语、提供简单解释、扩展学习推荐
- **中级**: 标准技术解释、提供深入学习资源、性能优化提示

### 教学内容库

- 编程概念解释（变量、函数、循环、条件等）
- 代码模板（常用代码片段）
- 学习路径（循序渐进学习计划）
- 练习题（巩固概念练习）

### 对话管理

- 多轮对话历史管理
- 学习进度追踪
- 上下文引用支持

## 技术栈

| 层级 | 技术栈 | 选择理由 |
|------|--------|---------|
| **前端层** | React + TypeScript + Vite | 生态丰富、组件库多、学习资源丰富、零基础用户容易上手 |
| **后端层** | Python + Flask + LangChain | LangChain生态丰富、支持多LLM切换、内置Agent框架功能 |
| **LLM层** | Claude API / OpenAI API | Claude擅长代码解释和概念解释、支持多LLM切换降低依赖风险 |
| **数据层** | PostgreSQL + Redis | PostgreSQL适合存储用户数据和教学内容、Redis适合缓存对话历史 |

## 项目结构

```
zergo-coding-agent/
├── backend/                    # 后端代码
│   ├── app/                    # 应用核心
│   │   ├── adapters/           # 难度适配器和Prompt构建器
│   │   ├── auth/              # 用户认证模块
│   │   ├── cache/             # 缓存模块
│   │   ├── chains/            # LangChain Chain实现
│   │   ├── cost/              # 成本控制系统
│   │   ├── database/          # 数据库模型
│   │   ├── llm/               # LLM客户端
│   │   ├── utils/             # 工具函数
│   │   ├── config.py          # 配置文件
│   │   ├── routes.py          # API路由
│   │   └── __init__.py        # 应用工厂
│   ├── tests/                 # 测试文件
│   ├── main.py                # 入口文件
│   ├── requirements.txt       # Python依赖
│   ├── Dockerfile             # 后端Docker配置
│   └── .dockerignore          # Docker忽略文件
├── frontend/                   # 前端代码
│   ├── src/                    # 源代码
│   │   ├── components/        # React组件
│   │   ├── hooks/             # 自定义Hooks
│   │   ├── pages/             # 页面组件
│   │   ├── services/          # API服务
│   │   ├── types/             # TypeScript类型
│   │   └── utils/             # 工具函数
│   ├── public/                # 静态资源
│   ├── package.json           # Node依赖
│   ├── vite.config.ts         # Vite配置
│   ├── Dockerfile             # 前端Docker配置
│   ├── nginx.conf             # Nginx配置
│   └── .dockerignore          # Docker忽略文件
├── docs/                       # 文档
├── .github/
│   └── workflows/
│       └── deploy.yml         # CI/CD配置
├── docker-compose.yml         # Docker Compose配置
├── .env.production            # 生产环境变量模板
└── README.md                  # 项目说明
```

## API接口列表

### 认证接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |

### 聊天接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/chat` | 发送聊天消息 | JWT |

### 模式接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/mode/switch` | 切换模式 | JWT |
| GET | `/api/mode/current` | 获取当前模式 | JWT |

### 缓存接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/cache/stats` | 获取缓存统计 | JWT |
| POST | `/api/cache/clear` | 清除所有缓存 | JWT |
| POST | `/api/cache/clear-expired` | 清除过期缓存 | JWT |

### 使用量接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/usage/stats` | 获取使用统计 | JWT |
| GET | `/api/usage/limit` | 检查API限制 | JWT |

### 用户等级接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/tier/upgrade` | 升级用户等级 | JWT |
| GET | `/api/tier/current` | 获取当前等级 | JWT |

### 健康检查

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health` | 健康检查 |

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (可选)

### 本地开发

#### 1. 克隆项目

```bash
git clone <repository-url>
cd zergo-coding-agent
```

#### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env
# 编辑 .env 文件，填入实际的配置值

# 启动后端服务
python main.py
```

#### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:5000

### Docker部署

#### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.production .env

# 编辑 .env 文件，填入实际的配置值
```

#### 2. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 3. 访问应用

- 前端: http://localhost:80
- 后端API: http://localhost:5000

#### 4. 停止服务

```bash
docker-compose down

# 同时删除数据卷
docker-compose down -v
```

### 生产环境部署

#### 1. 配置GitHub Secrets

在GitHub仓库设置中添加以下Secrets：

| Secret名称 | 描述 |
|-----------|------|
| `CLAUDE_API_KEY` | Claude API密钥 |
| `OPENAI_API_KEY` | OpenAI API密钥 |
| `PRODUCTION_HOST` | 生产服务器地址 |
| `PRODUCTION_USER` | SSH用户名 |
| `PRODUCTION_SSH_KEY` | SSH私钥 |
| `PRODUCTION_PATH` | 服务器项目路径 |
| `PRODUCTION_URL` | 生产环境URL |

#### 2. 配置服务器

确保服务器已安装：
- Docker
- Docker Compose
- Git

#### 3. 自动部署

推送到 `main` 分支将自动触发CI/CD流程：
1. 运行测试
2. 构建Docker镜像
3. 部署到生产服务器

## 测试说明

### 后端测试

```bash
cd backend

# 运行所有测试
pytest tests/

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_routes.py
```

### 前端测试

```bash
cd frontend

# 运行lint检查
npm run lint

# 构建项目
npm run build
```

## 环境变量说明

### 后端环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL连接URL | - |
| `REDIS_URL` | Redis连接URL | - |
| `CLAUDE_API_KEY` | Claude API密钥 | - |
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `JWT_SECRET_KEY` | JWT签名密钥 | - |
| `SECRET_KEY` | Flask密钥 | - |
| `FREE_TIER_API_LIMIT` | 免费用户API限制 | 50 |
| `PAID_TIER_API_LIMIT` | 付费用户API限制 | 500 |
| `DEBUG` | 调试模式 | False |
| `HOST` | 监听地址 | 0.0.0.0 |
| `PORT` | 监听端口 | 5000 |

## 贡献指南

欢迎贡献代码、报告问题或提出建议。请查看 Issues 页面了解更多。

## 许可证

MIT License