#!/bin/bash

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=== Database Backup ==="

# 创建备份目录
mkdir -p $BACKUP_DIR

# PostgreSQL备份
docker exec zero-basis-postgres pg_dump -U coding_agent coding_agent_db > $BACKUP_DIR/db_backup_$DATE.sql

# Redis备份
docker exec zero-basis-redis redis-cli BGSAVE
docker cp zero-basis-redis:/data/dump.rdb $BACKUP_DIR/redis_backup_$DATE.rdb

echo "Backup completed:"
echo "Database: $BACKUP_DIR/db_backup_$DATE.sql"
echo "Redis: $BACKUP_DIR/redis_backup_$DATE.rdb"

# 清理旧备份（保留最近7天）
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete

echo "Old backups cleaned"