# backend/app/__init__.py

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config

def create_app():
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(Config)

    # 初始化CORS
    CORS(app)

    # 初始化JWT
    jwt = JWTManager(app)

    # 注册路由（稍后添加）
    # from app.routes import register_routes
    # register_routes(app)

    return app