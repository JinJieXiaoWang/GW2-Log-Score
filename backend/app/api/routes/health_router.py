#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查相关API路由
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="健康检查", description="检查服务是否正常运行")
async def health_check():
    """
    健康检查端点

    Returns:
        服务状态
    """
    return {"status": "ok", "message": "Service is running"}
