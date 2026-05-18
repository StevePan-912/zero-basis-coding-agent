# backend/app/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM API配置
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')

    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    # 成本控制配置
    FREE_TIER_API_LIMIT = int(os.getenv('FREE_TIER_API_LIMIT', 50))
    PAID_TIER_API_LIMIT = int(os.getenv('PAID_TIER_API_LIMIT', 500))

    # Flask配置
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))