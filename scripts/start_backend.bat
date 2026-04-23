@echo off

REM 启动脚本 for GW2 Log Score

echo ==================================
echo GW2日志评分系统启动脚本
echo ==================================

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    echo 错误: 未找到Python解释器
    pause
    exit /b 1
)

echo 使用Python解释器: %PYTHON_CMD%

REM 检查并安装依赖
echo 检查依赖...
if not exist "requirements.txt" (
    echo 错误: 未找到requirements.txt文件
    pause
    exit /b 1
)

%PYTHON_CMD% -m pip install -r requirements.txt

REM 检查.env文件
if not exist ".env" (
    echo 警告: 未找到.env文件，使用默认配置
    if exist ".env.example" (
        echo 从.env.example创建.env文件...
        copy .env.example .env
    )
)

REM 启动后端服务
echo 启动后端服务...
echo 服务将在 http://0.0.0.0:8000 上运行
echo 按 Ctrl+C 停止服务
echo ==================================

%PYTHON_CMD% src/main.py --serve

pause
