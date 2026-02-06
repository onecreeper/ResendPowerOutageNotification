@echo off
REM Docker 快速启动脚本 - Windows
REM 用于快速配置和启动电力监控系统

echo ============================================================
echo       电力监控系统 - Docker 快速启动工具
echo ============================================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Docker，请先安装 Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [检查] Docker 已安装
docker --version
echo.

REM 检查 docker-compose 是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 docker-compose
    pause
    exit /b 1
)

echo [检查] docker-compose 已安装
docker-compose --version
echo.

REM 检查 .env 文件
if not exist ".env" (
    echo [提示] 未找到 .env 文件
    echo.
    echo 正在从 .env.example 创建 .env 文件...
    copy .env.example .env >nul
    echo.
    echo ============================================================
    echo [重要] 请编辑 .env 文件并填写你的配置
    echo ============================================================
    echo.
    echo 必需配置项:
    echo   1. RESEND_API_KEY       - 你的 Resend API Key
    echo   2. SENDER_FROM_ADDRESS  - 发件人地址（域名需在 Resend 验证）
    echo   3. RECIPIENT_EMAIL      - 收件人邮箱
    echo.
    notepad .env
    echo.
    set /p CONTINUE="配置完成后，按 Enter 继续，或输入 q 退出: "
    if /i "%CONTINUE%"=="q" (
        echo 取消启动
        pause
        exit /b 0
    )
) else (
    echo [检查] .env 文件已存在
)

echo.
echo ============================================================
echo 开始构建和启动服务...
echo ============================================================
echo.

REM 构建镜像
echo [步骤 1/3] 构建 Docker 镜像...
docker-compose build
if %errorlevel% neq 0 (
    echo [错误] 镜像构建失败
    pause
    exit /b 1
)
echo [完成] 镜像构建成功
echo.

REM 启动服务
echo [步骤 2/3] 启动服务...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [错误] 服务启动失败
    pause
    exit /b 1
)
echo [完成] 服务启动成功
echo.

REM 检查服务状态
echo [步骤 3/3] 检查服务状态...
docker-compose ps
echo.

echo ============================================================
echo 服务启动完成！
echo ============================================================
echo.
echo 常用命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose stop
echo   重启服务: docker-compose restart
echo   删除服务: docker-compose down
echo.
echo 详细文档: README.md
echo 测试指南: TEST_GUIDE.md
echo.
pause