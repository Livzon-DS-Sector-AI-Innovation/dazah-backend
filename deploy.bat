@echo off
chcp 65001 >nul
REM ========================================
REM Dazah 项目 Docker 一键部署 (Windows)
REM ========================================

echo ========================================
echo   Dazah 项目 Docker 一键部署
echo ========================================
echo.

REM 检查 Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker 未安装
    pause
    exit /b 1
)

REM 检查 Docker Compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker Compose 未安装
    pause
    exit /b 1
)

REM 确认部署
echo 将执行以下操作:
echo   1. 构建并启动 PostgreSQL
echo   2. 构建并启动 Redis
echo   3. 构建并启动后端服务
echo   4. 构建并启动前端服务
echo.
set /p confirm=是否继续? (y/n):
if /i not "%confirm%"=="y" (
    echo 部署已取消
    pause
    exit /b 0
)

REM 创建环境变量文件
if not exist .env (
    echo 创建 .env 文件...
    copy .env.template .env
    echo 请编辑 .env 文件设置密码
)

REM 创建 SSL 目录
if not exist ssl mkdir ssl

REM 构建镜像
echo.
echo 开始构建镜像...
docker compose build

REM 启动服务
echo.
echo 启动服务...
docker compose up -d

REM 等待启动
echo.
echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查状态
echo.
echo 检查服务状态...
docker compose ps

echo.
echo ========================================
echo   部署完成!
echo ========================================
echo.
echo 访问地址:
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo 常用命令:
echo   查看日志: docker compose logs -f
echo   停止服务: docker compose down
echo   重启服务: docker compose restart
echo ========================================
pause
