#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GW2 Log Score 主应用程序

启动完整的 GW2 日志评分系统后端服务
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src'))

# 导入API路由
from src.api.api import router as api_router

# 创建FastAPI应用
app = FastAPI(
    title="GW2 Log Score API",
    version="1.0.0",
    docs_url="/api/docs"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api")

# 健康检查端点
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    
    # 获取端口配置
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting GW2 Log Score API on {host}:{port}...")
    print(f"API Documentation: http://{host}:{port}/api/docs")
    
    uvicorn.run(app, host=host, port=port)
