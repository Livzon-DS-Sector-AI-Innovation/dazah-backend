# ========================================
# 一键部署脚本 - Docker 部署
# ========================================
# 使用方法:
#   chmod +x deploy.sh
#   ./deploy.sh

set -e

echo "========================================"
echo "  Dazah 项目 Docker 一键部署"
echo "========================================"

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "错误: Docker Compose 未安装"
    exit 1
fi

# 确认部署
echo ""
echo "将执行以下操作:"
echo "  1. 构建并启动 PostgreSQL"
echo "  2. 构建并启动 Redis"
echo "  3. 构建并启动后端服务"
echo "  4. 构建并启动前端服务"
echo ""
read -p "是否继续? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "部署已取消"
    exit 0
fi

# 创建环境变量文件（如果不存在）
if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cp .env.template .env
    echo "请编辑 .env 文件设置密码"
fi

# 创建 SSL 证书目录（可选）
mkdir -p ssl

# 构建并启动服务
echo ""
echo "开始构建镜像..."
docker compose build

echo ""
echo "启动服务..."
docker compose up -d

# 等待服务健康
echo ""
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "检查服务状态..."
docker compose ps

echo ""
echo "========================================"
echo "  部署完成!"
echo "========================================"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:3000"
echo "  后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "常用命令:"
echo "  查看日志: docker compose logs -f"
echo "  停止服务: docker compose down"
echo "  重启服务: docker compose restart"
echo "  进入后端: docker compose exec backend sh"
echo "========================================"
