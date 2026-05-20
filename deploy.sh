#!/bin/bash

echo "=== Zero-Basis Coding Agent Production Deployment ==="

# 检查环境变量
if [ ! -f .env.production ]; then
    echo "Error: .env.production file not found"
    exit 1
fi

# 加载环境变量
export $(cat .env.production | xargs)

# 拉取最新代码
echo "Pulling latest code..."
git pull origin main

# 停止现有服务
echo "Stopping existing services..."
docker-compose down

# 清理旧数据
echo "Cleaning old Docker images..."
docker system prune -f

# 构建新镜像
echo "Building new Docker images..."
docker-compose build

# 启动服务
echo "Starting services..."
docker-compose up -d

# 等待服务启动
echo "Waiting for services to start..."
sleep 10

# 健康检查
echo "Running health checks..."

# 检查后端健康
BACKEND_HEALTH=$(curl -s http://localhost:5000/api/health | grep -c "healthy")
if [ $BACKEND_HEALTH -eq 0 ]; then
    echo "Error: Backend health check failed"
    docker-compose logs backend
    exit 1
fi

# 检查前端健康
FRONTEND_HEALTH=$(curl -s http://localhost:80 | grep -c "html")
if [ $FRONTEND_HEALTH -eq 0 ]; then
    echo "Error: Frontend health check failed"
    docker-compose logs frontend
    exit 1
fi

echo "=== Deployment Successful ==="
echo "Frontend: http://localhost:80"
echo "Backend API: http://localhost:5000"
echo "API Health: http://localhost:5000/api/health"