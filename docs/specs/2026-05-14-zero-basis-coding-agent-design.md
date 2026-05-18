# 零基础编程Agent技术方案文档

## 项目概述

**项目名称：** 零基础编程Agent（Engineering Learning Agent）

**核心定位：** 帮助完全零基础的初学者学习编程概念并完成实际代码开发任务的双模式智能Agent系统

**目标用户：** 完全零基础的初学者（从未写过代码，需要从最基础概念开始学习）

**主要用途：** 两者兼顾 - 学习编程概念和完成实际开发任务

**约束条件：** 无特殊限制，可自由选择最佳技术方案

---

## 系统架构设计

### 整体架构

```
四层架构：

用户界面层（前端）
  ↓ HTTP/REST API

后端服务层（Agent核心）
  ↓ LLM API调用

LLM服务层（智能引擎）
  ↓ 数据访问

数据存储层（持久化）
```

### 技术栈选择

| 层级 | 技术栈 | 选择理由 |
|------|--------|---------|
| **前端层** | React + TypeScript | 生态丰富、组件库多、学习资源丰富、零基础用户容易上手、适合快速开发Web界面 |
| **后端层** | Python + LangChain | LangChain生态丰富、支持多LLM切换、内置Agent框架功能、适合长期维护、可定制性强 |
| **LLM层** | Claude API / OpenAI API | Claude擅长代码解释和概念解释、适合教学场景、支持多LLM切换降低依赖风险 |
| **数据层** | PostgreSQL + Redis | PostgreSQL适合存储用户数据和教学内容、Redis适合缓存对话历史和会话状态 |

### 技术栈对比分析

**为什么选择LangChain而非Claude Agent SDK：**

| 维度 | LangChain | Claude Agent SDK | 选择理由 |
|------|-----------|------------------|---------|
| 多LLM支持 | ✅ 支持多种LLM | ❌ 仅支持Claude | 降低单一依赖风险，可根据成本和性能切换LLM |
| 功能完整度 | ✅ 高（内置Memory、Tools、Chains） | ✅ 高 | LangChain功能更丰富，适合长期维护 |
| 生态成熟度 | ✅ 成熟（大量案例） | ⚠️ 较新（生态较小） | LangChain有更多参考案例和社区支持 |
| 长期维护成本 | ⚠️ 中高（框架更新频繁） | ⚠️ 中 | LangChain适合长期项目，框架更新是可接受的维护成本 |

**为什么选择独立后端而非Next.js全栈：**

| 维度 | 独立后端 | Next.js全栈 | 选择理由 |
|------|---------|------------|---------|
| API密钥安全性 | ✅ 安全（存储在后端） | ⚠️ 中等（API路由可暴露） | Claude API密钥需要安全存储，独立后端更安全 |
| 用户管理功能 | ✅ 完整（独立用户系统） | ⚠️ 需额外实现 | 支持用户认证、学习进度追踪、成本控制 |
| 成本控制能力 | ✅ 强（后端控制API调用） | ⚠️ 中（前端可能绕过） | 独立后端可以精确控制API调用次数和成本 |
| 扩展性 | ✅ 高（独立服务扩展） | ⚠️ 中（全栈限制） | 适合未来扩展更多功能模块 |

---

## 核心功能模块设计

### 1. 模式切换系统

**设计目标：** 用户手动切换教学模式/实用模式，根据需求灵活使用

**模块架构：**

```python
# LangChain模式切换Chain设计

class ModeSwitchingChain:
    """
    双模式切换系统
    - 教学模式：详细解释概念、代码逐行解释、学习路径推荐
    - 实用模式：快速生成代码、简化解释、一键部署运行
    """

    def __init__(self):
        self.teaching_chain = TeachingChain()
        self.practical_chain = PracticalChain()

    def switch_mode(self, mode: str, user_input: str, difficulty: str):
        """
        切换模式并执行对应Chain

        Args:
            mode: 'teaching' 或 'practical'
            user_input: 用户输入需求
            difficulty: 用户难度等级
        """
        if mode == 'teaching':
            return self.teaching_chain.run(user_input, difficulty)
        elif mode == 'practical':
            return self.practical_chain.run(user_input, difficulty)
```

**教学模式Chain设计：**

```python
class TeachingChain(Chain):
    """
    教学模式Chain

    输出格式：
    - 概念解释：详细解释编程概念（使用类比）
    - 代码生成：生成代码 + 逐行解释
    - 学习建议：推荐下一步学习内容
    """

    def run(self, user_input: str, difficulty: str):
        # Step 1: 分析用户需求，识别涉及的概念
        concepts = self.identify_concepts(user_input)

        # Step 2: 概念解释prompt（根据难度调整）
        concept_prompt = self.build_concept_prompt(concepts, difficulty)

        # Step 3: 代码生成prompt（包含逐行解释）
        code_prompt = self.build_code_prompt(user_input, difficulty)

        # Step 4: 学习建议prompt（推荐下一步学习内容）
        learning_prompt = self.build_learning_prompt(concepts, difficulty)

        # Step 5: 组合Chain执行
        return self.execute_chain([
            concept_prompt,
            code_prompt,
            learning_prompt
        ])
```

**实用模式Chain设计：**

```python
class PracticalChain(Chain):
    """
    实用模式Chain

    输出格式：
    - 快速代码生成：完整可执行代码
    - 简化解释：核心功能说明（3-5句话）
    - 使用建议：如何运行和使用代码
    """

    def run(self, user_input: str, difficulty: str):
        # Step 1: 快速生成代码
        code_prompt = self.build_quick_code_prompt(user_input)

        # Step 2: 简化解释prompt
        simple_explanation_prompt = self.build_simple_explanation_prompt()

        # Step 3: 使用建议prompt
        usage_prompt = self.build_usage_prompt()

        # Step 4: 组合Chain执行
        return self.execute_chain([
            code_prompt,
            simple_explanation_prompt,
            usage_prompt
        ])
```

**模式切换Prompt模板：**

```python
# 教学模式Prompt模板

TEACHING_CONCEPT_PROMPT = """
你是一位零基础编程导师，正在帮助完全零基础的初学者理解编程概念。

用户需求：{user_input}
涉及概念：{concepts}
用户难度等级：{difficulty}

请详细解释以下编程概念，要求：
1. 使用类比解释（例如：变量就像一个盒子，用来存储东西）
2. 避免技术术语，或使用时提供简单解释
3. 提供可视化示例（如流程图、数据流向图）
4. 标注概念难度等级（简单/中等/复杂）

概念解释格式：
## 概念解释
### {concept_name}（难度：{difficulty_level}）
**类比解释：** {analogy}
**技术解释：** {technical_explanation}
**示例：** {example}
"""

TEACHING_CODE_PROMPT = """
你是一位零基础编程导师，正在帮助完全零基础的初学者生成代码并逐行解释。

用户需求：{user_input}
用户难度等级：{difficulty}

请生成代码并逐行解释，要求：
1. 使用最简单的实现方式（避免复杂技巧）
2. 每行代码添加详细注释（解释WHY而非WHAT）
3. 标注代码难度等级（简单/中等/复杂）
4. 提供可修改的建议（让用户参与代码调整）

代码输出格式：
## 代码实现
### 代码（难度：{difficulty_level}）
```{language}
{code_with_comments}
```

### 逐行解释
{line_by_line_explanation}

### 可修改建议
{modification_suggestions}
"""

# 实用模式Prompt模板

PRACTICAL_CODE_PROMPT = """
你是一位智能代码助手，正在帮助用户快速生成可执行代码。

用户需求：{user_input}

请快速生成完整可执行代码，要求：
1. 代码完整且可直接运行
2. 包含必要的错误处理
3. 标注依赖包和安装命令

代码输出格式：
## 代码（可直接运行）
```{language}
{complete_code}
```

## 依赖安装
{dependency_installation}
"""

PRACTICAL_EXPLANATION_PROMPT = """
请用3-5句话简化解释代码的核心功能，避免深入细节。

简化解释格式：
## 核心功能（简化版）
{simple_explanation}
"""
```

---

### 2. 难度适配系统

**设计目标：** 根据用户技术水平自动调整代码复杂度和解释详细度

**难度等级定义：**

| 等级 | Prompt特点 | 代码风格 | 解释详细度 |
|------|-----------|---------|-----------|
| **零基础** | 使用类比、避免技术术语、提供基础概念链接 | 最简单实现、大量注释、标注难度等级 | 概念解释 + 逐行代码解释 + 学习建议 |
| **初级** | 适度技术术语、提供简单解释、扩展学习推荐 | 标准实现、关键注释、提供优化建议 | 核心概念解释 + 关键代码解释 + 扩展学习 |
| **中级** | 标准技术解释、提供深入学习资源、性能优化提示 | 最佳实践实现、关键逻辑注释、扩展思考 | 技术解释 + 关键逻辑说明 + 性能优化提示 |

**难度判断机制：**

```python
class DifficultyAdapter:
    """
    难度适配系统

    判断方式：
    1. 用户手动设置（初始水平）
    2. 根据历史交互自动调整（学习进度）
    """

    def assess_difficulty(self, user_id: str):
        """
        评估用户难度等级

        基于因素：
        - 用户手动设置的初始水平
        - 历史对话中使用的术语水平
        - 用户提问的复杂度
        - 用户代码修改的复杂度
        """
        # 获取用户历史数据
        user_data = self.get_user_data(user_id)

        # 计算难度分数（0-100）
        difficulty_score = self.calculate_difficulty_score(user_data)

        # 映射到难度等级
        if difficulty_score < 30:
            return 'beginner'
        elif difficulty_score < 70:
            return 'intermediate'
        else:
            return 'advanced'

    def calculate_difficulty_score(self, user_data):
        """
        计算难度分数

        评分维度：
        - 历史提问复杂度（0-40分）
        - 代码修改复杂度（0-30分）
        - 使用术语水平（0-20分）
        - 学习进度（0-10分）
        """
        score = 0

        # 历史提问复杂度
        question_complexity = user_data['question_complexity_history']
        score += min(question_complexity * 4, 40)

        # 代码修改复杂度
        code_modification_complexity = user_data['code_modification_complexity_history']
        score += min(code_modification_complexity * 3, 30)

        # 使用术语水平
        terminology_level = user_data['terminology_usage_level']
        score += min(terminology_level * 2, 20)

        # 学习进度
        learning_progress = user_data['concepts_learned_count']
        score += min(learning_progress, 10)

        return score
```

**难度适配Prompt动态生成：**

```python
class DifficultyPromptBuilder:
    """
    根据难度等级动态生成Prompt
    """

    def build_prompt(self, base_prompt: str, difficulty: str):
        """
        动态调整Prompt内容

        Args:
            base_prompt: 基础Prompt模板
            difficulty: 'beginner', 'intermediate', 'advanced'
        """
        if difficulty == 'beginner':
            # 添加零基础友好指令
            return self.add_beginner_instructions(base_prompt)
        elif difficulty == 'intermediate':
            # 添加初级友好指令
            return self.add_intermediate_instructions(base_prompt)
        else:
            # 添加中级友好指令
            return self.add_advanced_instructions(base_prompt)

    def add_beginner_instructions(self, base_prompt):
        """
        添加零基础友好指令

        指令内容：
        - 使用类比解释概念（如：变量就像盒子）
        - 避免技术术语（如：避免说"异步"，说"同时做两件事"）
        - 提供可视化示例（如：流程图）
        - 标注概念难度等级（简单/中等/复杂）
        - 提供基础概念学习链接
        """
        instructions = """
重要指令（零基础用户）：
1. 使用类比解释所有概念（例如：变量就像盒子，函数就像机器）
2. 避免技术术语，如必须使用请提供简单解释
3. 提供可视化示例（如流程图、数据流向图）
4. 标注概念难度等级（简单/中等/复杂）
5. 提供基础概念学习链接
"""
        return base_prompt + instructions

    def add_intermediate_instructions(self, base_prompt):
        """
        添加初级友好指令

        指令内容：
        - 适度使用技术术语（提供简单解释）
        - 提供扩展学习推荐（下一步学习内容）
        - 标注代码优化建议（如何改进代码）
        - 提供简单性能提示（代码运行效率）
        """
        instructions = """
重要指令（初级用户）：
1. 适度使用技术术语，使用时提供简单解释
2. 提供扩展学习推荐（下一步学习内容）
3. 标注代码优化建议（如何改进代码）
4. 提供简单性能提示（代码运行效率）
"""
        return base_prompt + instructions

    def add_advanced_instructions(self, base_prompt):
        """
        添加中级友好指令

        指令内容：
        - 使用标准技术术语（不需要过度解释）
        - 提供深入学习资源（外部文档链接）
        - 提供性能优化提示（内存、并发、算法优化）
        - 提供扩展思考（边界条件、异常处理、并发问题）
        """
        instructions = """
重要指令（中级用户）：
1. 使用标准技术术语，不需要过度解释
2. 提供深入学习资源（外部文档链接）
3. 提供性能优化提示（内存、并发、算法优化）
4. 提供扩展思考（边界条件、异常处理、并发问题）
"""
        return base_prompt + instructions
```

---

### 3. 教学内容库系统

**设计目标：** 存储和检索编程教学内容，减少API调用次数，提高响应速度

**教学内容库结构：**

```python
# 教学内容库数据结构

class TeachingContentDatabase:
    """
    教学内容库

    存储内容：
    - 编程概念解释（变量、函数、循环、条件等）
    - 代码模板（常用代码片段）
    - 学习路径（循序渐进学习计划）
    - 练习题（巩固概念练习）
    """

    # PostgreSQL表结构设计

    CONCEPTS_TABLE = """
    CREATE TABLE programming_concepts (
        id SERIAL PRIMARY KEY,
        concept_name VARCHAR(100) NOT NULL,
        difficulty_level VARCHAR(20) NOT NULL, -- 'beginner', 'intermediate', 'advanced'
        analogy_explanation TEXT NOT NULL,
        technical_explanation TEXT NOT NULL,
        visual_example TEXT, -- 流程图、数据流向图描述
        related_concepts JSONB, -- 相关概念列表
        learning_links JSONB, -- 学习资源链接
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """

    CODE_TEMPLATES_TABLE = """
    CREATE TABLE code_templates (
        id SERIAL PRIMARY KEY,
        template_name VARCHAR(100) NOT NULL,
        language VARCHAR(50) NOT NULL, -- 'python', 'javascript', etc.
        difficulty_level VARCHAR(20) NOT NULL,
        code_content TEXT NOT NULL,
        comments TEXT, -- 代码注释
        usage_scenario TEXT, -- 使用场景描述
        related_concepts JSONB, -- 涉及概念
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """

    LEARNING_PATHS_TABLE = """
    CREATE TABLE learning_paths (
        id SERIAL PRIMARY KEY,
        path_name VARCHAR(100) NOT NULL,
        target_difficulty VARCHAR(20) NOT NULL, -- 目标难度等级
        concepts_sequence JSONB NOT NULL, -- 概念学习顺序
        estimated_time INTEGER, -- 预估学习时间（小时）
        prerequisites JSONB, -- 前置知识要求
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
```

**教学内容检索策略：**

```python
class ContentRetrievalStrategy:
    """
    教学内容检索策略

    目标：
    - 优先从本地库检索（减少API调用）
    - 本地库无内容时调用LLM生成
    - 生成后存储到本地库（缓存）
    """

    def retrieve_concept_explanation(self, concept_name: str, difficulty: str):
        """
        检索概念解释

        检索顺序：
        1. PostgreSQL本地库检索
        2. Redis缓存检索
        3. LLM生成（并存储）
        """
        # Step 1: PostgreSQL检索
        local_content = self.query_local_db(concept_name, difficulty)
        if local_content:
            return local_content

        # Step 2: Redis缓存检索
        cached_content = self.query_redis_cache(concept_name, difficulty)
        if cached_content:
            return cached_content

        # Step 3: LLM生成（并存储）
        generated_content = self.generate_with_llm(concept_name, difficulty)

        # 存储到PostgreSQL和Redis
        self.store_to_local_db(generated_content)
        self.store_to_redis_cache(generated_content)

        return generated_content
```

---

### 4. 对话管理系统

**设计目标：** 管理用户对话历史，支持多轮对话，追踪学习进度

**对话管理Chain设计：**

```python
class ConversationManagementChain(Chain):
    """
    对话管理Chain

    功能：
    - 管理对话历史（ConversationBufferMemory）
    - 追踪学习进度（记录用户已学概念）
    - 支持上下文引用（用户可以引用之前对话）
    """

    def __init__(self):
        # LangChain Memory配置
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 学习进度追踪
        self.progress_tracker = LearningProgressTracker()

    def manage_conversation(self, user_id: str, user_input: str):
        """
        管理对话流程

        Args:
            user_id: 用户ID
            user_input: 用户输入
        """
        # Step 1: 加载用户对话历史
        chat_history = self.load_chat_history(user_id)

        # Step 2: 分析用户输入意图
        intent = self.analyze_intent(user_input, chat_history)

        # Step 3: 根据意图执行不同Chain
        response = self.execute_intent_chain(intent, user_input, chat_history)

        # Step 4: 更新对话历史
        self.update_chat_history(user_id, user_input, response)

        # Step 5: 更新学习进度
        self.progress_tracker.update(user_id, response)

        return response

    def analyze_intent(self, user_input: str, chat_history: list):
        """
        分析用户输入意图

        意图类型：
        - 新需求（从头开始）
        - 修改需求（基于之前对话）
        - 学习需求（只想学习概念）
        - 继续需求（继续之前任务）
        """
        # 使用LLM分析意图
        intent_prompt = f"""
分析用户意图：

用户输入：{user_input}
对话历史：{chat_history}

请判断用户意图类型：
1. 新需求：用户提出全新的需求
2. 修改需求：用户想修改之前的代码或解释
3. 学习需求：用户只想学习某个概念，不需要代码
4. 继续需求：用户想继续之前的任务

请输出意图类型和关键信息。
"""
        intent_response = self.llm.invoke(intent_prompt)
        return self.parse_intent(intent_response)
```

**学习进度追踪：**

```python
class LearningProgressTracker:
    """
    学习进度追踪系统

    功能：
    - 记录用户已学概念
    - 计算学习进度百分比
    - 推荐下一步学习内容
    """

    def update(self, user_id: str, response: dict):
        """
        更新学习进度

        从response中提取：
        - 涉及的概念列表
        - 用户理解程度（根据用户反馈）
        - 学习时间戳
        """
        # 提取涉及概念
        concepts = response.get('concepts_involved', [])

        # 更新用户学习记录
        for concept in concepts:
            self.record_concept_learning(user_id, concept)

    def get_progress(self, user_id: str):
        """
        获取学习进度

        返回：
        - 已学概念列表
        - 学习进度百分比
        - 推荐下一步学习内容
        """
        # 查询用户已学概念
        learned_concepts = self.query_learned_concepts(user_id)

        # 计算进度百分比
        total_concepts = self.get_total_concepts_count()
        progress_percentage = len(learned_concepts) / total_concepts * 100

        # 推荐下一步学习内容
        recommended_next = self.recommend_next_concepts(learned_concepts)

        return {
            'learned_concepts': learned_concepts,
            'progress_percentage': progress_percentage,
            'recommended_next': recommended_next
        }
```

---

## API接口设计

### REST API设计

**API端点设计：**

```
POST /api/v1/chat
描述：用户对话接口
请求参数：
{
  "user_id": "string",
  "user_input": "string",
  "mode": "teaching" | "practical",
  "difficulty": "beginner" | "intermediate" | "advanced"
}
响应格式：
{
  "response": "string",
  "concepts_involved": ["string"],
  "code_generated": "string",
  "learning_recommendation": "string"
}

GET /api/v1/progress/{user_id}
描述：获取用户学习进度
响应格式：
{
  "learned_concepts": ["string"],
  "progress_percentage": "number",
  "recommended_next": ["string"]
}

POST /api/v1/mode/switch
描述：切换模式
请求参数：
{
  "user_id": "string",
  "mode": "teaching" | "practical"
}
响应格式：
{
  "success": "boolean",
  "current_mode": "string"
}

POST /api/v1/difficulty/adjust
描述：调整难度等级
请求参数：
{
  "user_id": "string",
  "difficulty": "beginner" | "intermediate" | "advanced"
}
响应格式：
{
  "success": "boolean",
  "current_difficulty": "string"
}
```

---

## 数据结构设计

### PostgreSQL数据表设计

**用户表：**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    initial_difficulty VARCHAR(20) DEFAULT 'beginner',
    preferred_mode VARCHAR(20) DEFAULT 'teaching',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**对话历史表：**

```sql
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    conversation_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    mode VARCHAR(20), -- 'teaching' or 'practical'
    difficulty VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**学习进度表：**

```sql
CREATE TABLE learning_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    concept_name VARCHAR(100) NOT NULL,
    understanding_level VARCHAR(20), -- 'basic', 'intermediate', 'advanced'
    learned_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);
```

---

## 安全性设计

### API密钥安全存储

**策略：**
- Claude API密钥存储在后端环境变量中（不暴露给前端）
- 使用.env文件存储密钥（不提交到git）
- 生产环境使用密钥管理服务（AWS Secrets Manager、HashiCorp Vault）

**实现：**

```python
# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')
```

### 用户认证安全

**策略：**
- 使用JWT认证（jsonwebtoken）
- 密码使用bcrypt加盐哈希存储
- 支持GitHub OAuth登录（可选）

**实现：**

```python
# backend/auth.py

from flask_jwt_extended import JWTManager, create_access_token
import bcrypt

class AuthManager:
    def hash_password(self, password: str):
        """使用bcrypt加盐哈希"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password: str, hashed: str):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    def create_jwt_token(self, user_id: int):
        """创建JWT token"""
        return create_access_token(identity=user_id)
```

---

## 性能优化设计

### 响应缓存策略

**策略：**
- 相同问题的响应缓存到Redis（减少API调用）
- 教学内容缓存到Redis（提高检索速度）
- 用户对话历史缓存到Redis（快速加载历史）

**实现：**

```python
# backend/cache.py

import redis
import json

class ResponseCache:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def cache_response(self, key: str, response: dict, ttl: int = 3600):
        """缓存响应（默认1小时）"""
        self.redis_client.setex(key, ttl, json.dumps(response))

    def get_cached_response(self, key: str):
        """获取缓存响应"""
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None
```

### API调用优化

**策略：**
- 使用prompt caching（Claude API支持）
- 批量处理用户请求
- 减少重复prompt调用

**实现：**

```python
# backend/llm_optimizer.py

class LLMCallOptimizer:
    def optimize_prompt(self, prompt: str):
        """
        优化prompt以减少API调用成本

        优化方法：
        - 使用prompt caching（Claude API）
        - 减少prompt长度（去除冗余内容）
        - 合理使用system prompt
        """
        # 添加caching控制标记
        optimized_prompt = f"""
<!-- cache-control: {{"type": "ephemeral"}} -->
{prompt}
"""
        return optimized_prompt
```

---

## 测试方案设计

### 单元测试

**测试内容：**
- 模式切换功能测试
- 难度适配功能测试
- Prompt生成功能测试
- 对话管理功能测试

**测试示例：**

```python
# tests/test_mode_switching.py

import pytest
from chains import ModeSwitchingChain

def test_teaching_mode():
    """测试教学模式"""
    chain = ModeSwitchingChain()
    response = chain.switch_mode('teaching', '如何定义变量', 'beginner')

    assert '概念解释' in response
    assert '类比解释' in response
    assert '代码实现' in response
    assert '学习建议' in response

def test_practical_mode():
    """测试实用模式"""
    chain = ModeSwitchingChain()
    response = chain.switch_mode('practical', '创建一个简单的HTTP服务器', 'beginner')

    assert '代码（可直接运行）' in response
    assert '核心功能（简化版）' in response
    assert '依赖安装' in response
```

### 集成测试

**测试内容：**
- 前端到后端完整流程测试
- 用户认证流程测试
- 对话历史存储测试
- 学习进度追踪测试

---

## 成本控制方案

### API调用计数限制

**策略：**
- 每日API调用次数限制（免费用户：50次/天，付费用户：500次/天）
- 单次对话API调用次数限制（避免过度调用）
- 用户分级管理（根据付费情况调整限制）

**实现：**

```python
# backend/cost_control.py

class CostController:
    def check_api_limit(self, user_id: int):
        """检查用户API调用限制"""
        user_tier = self.get_user_tier(user_id)
        daily_limit = self.get_daily_limit(user_tier)

        current_usage = self.get_today_usage(user_id)

        if current_usage >= daily_limit:
            raise LimitExceededError(f"今日API调用次数已达上限（{daily_limit}次）")

    def increment_usage(self, user_id: int):
        """增加API调用计数"""
        self.redis_client.incr(f"api_usage:{user_id}:{today}")
```

---

## 风险评估

### 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Claude API服务中断 | 高 | 支持多LLM切换（OpenAI备用） |
| LangChain框架重大更新 | 中 | 使用稳定版本，避免使用最新功能 |
| PostgreSQL数据库故障 | 高 | 使用数据库备份和恢复机制 |
| Redis缓存失效 | 中 | 缓存失效时降级到直接查询数据库 |

### 成本风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| API调用成本过高 | 高 | 实施严格的API调用限制和缓存策略 |
| 数据库存储成本增长 | 中 | 定期清理过期对话历史 |
| 服务器资源成本 | 中 | 使用云服务弹性伸缩 |

### 安全风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| API密钥泄露 | 高 | 密钥存储在后端环境变量，使用密钥管理服务 |
| 用户数据泄露 | 高 | 使用HTTPS加密传输，数据库加密存储 |
| DDoS攻击 | 中 | 使用云服务DDoS防护 |

---

## 实现步骤概要

### Phase 1：后端核心开发（2周）

1. 搭建Python + LangChain框架
2. 实现模式切换系统
3. 实现难度适配系统
4. 实现教学内容库
5. 实现对话管理系统
6. 实现用户认证系统
7. 配置Claude API和OpenAI API
8. 配置PostgreSQL和Redis

### Phase 2：前端界面开发（1.5周）

1. 搭建React + TypeScript框架
2. 实现用户界面（教学模式/实用模式）
3. 实现对话界面
4. 实现学习进度展示
5. 实现难度选择界面
6. 实现模式切换界面
7. 连接后端API

### Phase 3：集成测试与优化（1周）

1. 前后端集成测试
2. 性能优化测试
3. 安全测试
4. 用户体验测试
5. Bug修复

### Phase 4：部署上线（0.5周）

1. 服务器部署
2. 数据库部署
3. API密钥配置
4. 监控配置
5. 用户反馈收集

---

## 下一步行动

1. ✅ 确认技术方案文档
2. 编写详细实现计划（使用writing-plans skill）
3. 开始Phase 1后端核心开发

---

**文档版本：** v1.0
**创建日期：** 2026-05-14
**作者：** Claude + StevePan-912