#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GW2 Log Score 主应用程序

启动完整的 GW2 日志评分系统后端服务
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.application import app
from app.config.config_loader import HOST, PORT

if __name__ == "__main__":
    import uvicorn
    
    # 获取端口配置
    port = int(os.getenv("PORT", PORT))
    host = os.getenv("HOST", HOST)
    
    print(f"Starting GW2 Log Score API on {host}:{port}...")
    print(f"API Documentation: http://{host}:{port}/api/docs")
    
    uvicorn.run(app, host=host, port=port)
