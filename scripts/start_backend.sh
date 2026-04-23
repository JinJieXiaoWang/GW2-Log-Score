#!/bin/bash

# 启动脚本 for GW2 Log Score

echo "=================================="
echo "GW2日志评分系统启动脚本"
echo "=================================="

# 检查Python是否可用
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "错误: 未找到Python解释器"
    exit 1
fi

echo "使用Python解释器: $PYTHON_CMD"

# 检查并安装依赖
echo "检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt文件"
    exit 1
fi

$PYTHON_CMD -m pip install -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，使用默认配置"
    if [ -f ".env.example" ]; then
        echo "从.env.example创建.env文件..."
        cp .env.example .env
    fi
fi

# 启动后端服务
echo "启动后端服务..."
echo "服务将在 http://0.0.0.0:8000 上运行"
echo "按 Ctrl+C 停止服务"
echo "=================================="

$PYTHON_CMD src/main.py --serve
