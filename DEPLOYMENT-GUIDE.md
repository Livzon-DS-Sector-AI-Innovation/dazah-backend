# Dazah 项目完整部署指南

## 服务器配置要求
- 系统：Ubuntu 22.04/24.04
- 配置：2核2G（最低） 推荐4G
- 端口：3000（前端）、8000（后端）

---

## 第一阶段：环境准备

### 1. 上传代码
```bash
# 使用 FinalShell 或 scp 上传 Dazah-Deploy-v2.zip
scp Dazah-Deploy-v2.zip root@8.145.32.153:/opt/
```

### 2. 解压代码
```bash
cd /opt
unzip Dazah-Deploy-v2.zip
cd dahzah-deploy
```

---

## 第二阶段：安装系统依赖

### 3. 更新系统
```bash
apt-get update && apt-get upgrade -y
```

### 4. 安装基础工具
```bash
apt-get install -y curl wget unzip postgresql postgresql-contrib redis-server
```

### 5. 安装 Node.js
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
npm install -g pnpm
node -v && pnpm -v
```

### 6. 安装 Python 依赖
```bash
pip install --break-system-packages \
  fastapi uvicorn sqlalchemy asyncpg alembic \
  pydantic pydantic-settings redis python-dotenv \
  httpx psycopg-binary pg8000 openpyxl \
  python-docx mammoth beautifulsoup4 python-multipart
```

---

## 第三阶段：配置数据库

### 7. 启动 PostgreSQL
```bash
systemctl start postgresql
systemctl enable postgresql
```

### 8. 创建数据库和用户
```bash
su - postgres -c "psql -c \"CREATE USER dazah WITH PASSWORD 'Dazah@2024!Secure';\""
su - postgres -c "psql -c \"CREATE DATABASE dazah OWNER dazah;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE dazah TO dazah;\""

# 验证
su - postgres -c "psql -d dazah -c 'SELECT 1;'"
```

### 9. 启动 Redis
```bash
systemctl start redis-server
systemctl enable redis-server
redis-cli ping
```

---

## 第四阶段：部署后端

### 10. 配置后端环境变量
```bash
cd /opt/dazah-deploy/dazah-backend

cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://dazah:Dazah@2024!Secure@localhost:5432/dazah
REDIS_URL=redis://localhost:6379/0
DEBUG=false
SECRET_KEY=dazah-production-secret-key-2024
APP_ENV=production
EOF
```

### 11. 修复代码（添加缺失导入）
```bash
sed -i '7 a from sqlalchemy.ext.asyncio import AsyncSession' app/api/v1/ai_config_api.py
```

### 12. 启动后端
```bash
nohup /usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
sleep 8

# 验证
curl http://localhost:8000/
netstat -tlnp | grep 8000
```

---

## 第五阶段：部署前端

### 13. 配置前端环境
```bash
cd /opt/dazah-deploy/dazah-frontend
echo 'HOST=0.0.0.0' >> .env.local
```

### 14. 安装前端依赖
```bash
pnpm install
```

### 15. 启动前端
```bash
nohup pnpm run dev > frontend.log 2>&1 &
sleep 15

# 验证
netstat -tlnp | grep 3000
```

---

## 第六阶段：网络安全配置

### 16. 配置防火墙
```bash
# 方案1：关闭防火墙（测试环境）
ufw disable

# 方案2：开放指定端口（生产环境）
ufw allow 3000/tcp
ufw allow 8000/tcp
```

### 17. 配置阿里云安全组
登录阿里云控制台 → ECS → 安全组 → 入方向规则：
| 协议 | 端口 | 来源 |
|------|------|------|
| TCP | 3000/3000 | 0.0.0.0/0 |
| TCP | 8000/8000 | 0.0.0.0/0 |

---

## 第七阶段：验证部署

### 18. 访问应用
- 前端：http://8.145.32.153:3000
- 后端：http://8.145.32.153:8000
- API文档：http://8.145.32.153:8000/docs

---

## 第八阶段：运维命令

### 查看服务状态
```bash
netstat -tlnp | grep -E "3000|8000"
```

### 查看日志
```bash
# 后端日志
tail -f /opt/dazah-deploy/dazah-backend/backend.log

# 前端日志
tail -f /opt/dazah-deploy/dazah-frontend/frontend.log
```

### 重启服务
```bash
# 重启后端
pkill -f uvicorn
cd /opt/dazah-deploy/dazah-backend
nohup /usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# 重启前端
pkill -f "next dev"
cd /opt/dazah-deploy/dazah-frontend
nohup pnpm run dev > frontend.log 2>&1 &
```

### 停止服务
```bash
pkill -f uvicorn
pkill -f "next dev"
```

---

## 第九阶段：Nginx配置（可选）

### 19. 安装 Nginx
```bash
apt-get install -y nginx
```

### 20. 配置反向代理
```bash
cat > /etc/nginx/sites-available/dazah << 'EOF'
server {
    listen 80;
    server_name 8.145.32.153;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_read_timeout 300s;
    }
}
EOF

ln -s /etc/nginx/sites-available/dazah /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl enable nginx
```

---

## 第十阶段：SSL配置（可选）

### 21. 安装 Certbot
```bash
apt-get install -y certbot python3-certbot-nginx
```

### 22. 获取证书
```bash
# 需要有域名
certbot --nginx -d your-domain.com
```

### 23. 自动续期
```bash
certbot renew --dry-run
```

---

## 故障排查

### 数据库连接失败
```bash
su - postgres -c "psql -d dazah -c 'SELECT 1;'"
```

### 端口被占用
```bash
lsof -i :3000
lsof -i :8000
```

### 服务启动失败
```bash
cat backend.log
cat frontend.log
```

### 重置所有数据
```bash
systemctl stop postgresql redis-server
rm -rf /var/lib/postgresql/data/*
systemctl start postgresql
# 重新执行数据库初始化
```
