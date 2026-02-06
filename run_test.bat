@echo off
REM 电力监控系统 - 测试运行脚本
REM 用于 Windows 环境下快速运行场景测试

echo ============================================================
echo       电力监控系统 - 场景测试工具 (Windows)
echo ============================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [检查] Python 已安装
echo.

REM 检查依赖
echo [检查] 检查依赖包...
pip show resend >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未找到 resend 包，正在安装...
    pip install resend
    if %errorlevel% neq 0 (
        echo [错误] 安装依赖失败
        pause
        exit /b 1
    )
)
echo [完成] 依赖检查通过
echo.

REM 检查环境变量
echo [检查] 环境变量配置...
if "%RESEND_API_KEY%"=="" (
    echo [警告] RESEND_API_KEY 未设置
    echo.
    echo 请设置环境变量：
    echo   set RESEND_API_KEY=re_your_api_key
    echo   set SENDER_FROM_ADDRESS=测试 ^<alerts@your-domain.com^>
    echo   set RECIPIENT_EMAIL=your@email.com
    echo.
    echo 或者使用本脚本设置环境变量（见下文）
    echo.
    set /p CONTINUE="是否继续运行测试？(y/n): "
    if /i not "%CONTINUE%"=="y" (
        echo 取消测试
        pause
        exit /b 0
    )
) else (
    echo [完成] 环境变量已配置
    echo   RESEND_API_KEY: %RESEND_API_KEY:~0,10%...
    echo   SENDER_FROM_ADDRESS: %SENDER_FROM_ADDRESS%
    echo   RECIPIENT_EMAIL: %RECIPIENT_EMAIL%
)

echo.
echo ============================================================
echo 开始运行测试脚本...
echo ============================================================
echo.

REM 运行测试脚本
python test_scenarios.py

echo.
echo ============================================================
echo 测试脚本已退出
echo ============================================================
pause