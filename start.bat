@echo off
echo === 服务器断电和网络监控系统 ===
echo 功能: 断电检测 + 网络状态监控 + 邮件通知

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未安装，请先安装Docker
    pause
    exit /b 1
)

REM 检查docker-compose是否可用
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo 错误: docker-compose未安装，请先安装docker-compose
        pause
        exit /b 1
    ) else (
        set DOCKER_COMPOSE_CMD=docker-compose
    )
) else (
    set DOCKER_COMPOSE_CMD=docker compose
)

REM 检查配置文件
if not exist docker-compose.yml (
    echo 错误: docker-compose.yml 文件不存在
    pause
    exit /b 1
)

REM 检查是否配置了Resend API密钥
findstr /C:"re_xxxxxxxxxxxxxxxxxxxxxx" docker-compose.yml >nul
if not errorlevel 1 (
    echo 警告: 请先配置Resend API密钥和其他环境变量
    echo 编辑 docker-compose.yml 文件，修改以下配置:
    echo   - RESEND_API_KEY
    echo   - SENDER_FROM_ADDRESS
    echo   - RECIPIENT_EMAIL
    echo   - SERVER_NAME
    echo.
    set /p CONTINUE="是否继续启动？(y/N): "
    if /i not "%CONTINUE%"=="y" (
        if /i not "%CONTINUE%"=="Y" (
            exit /b 0
        )
    )
)

echo 启动监控服务...
%DOCKER_COMPOSE_CMD% up -d

echo 服务已启动！
echo 查看日志: %DOCKER_COMPOSE_CMD% logs -f
echo 停止服务: %DOCKER_COMPOSE_CMD% down
echo.
echo 监控功能:
echo   - 每60秒检测一次网络状态
echo   - 断电后恢复时发送邮件通知
echo   - 网络状态变化时发送邮件通知
echo   - 支持内网和外网连接检测

pause
