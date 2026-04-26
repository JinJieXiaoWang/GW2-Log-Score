#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由初始化
"""

from fastapi import APIRouter
from app.api.routes.log_router import router as log_router
from app.api.routes.score_router import router as score_router
from app.api.routes.profession_router import router as profession_router
from app.api.routes.dictionary_router import router as dictionary_router
from app.api.routes.health_router import router as health_router
from app.api.routes.i18n_router import router as i18n_router
from app.api.routes.attendance_router import router as attendance_router

# 创建主路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(log_router, tags=["logs"])
api_router.include_router(score_router, tags=["scores"])
api_router.include_router(profession_router, tags=["professions"])
api_router.include_router(dictionary_router, tags=["dictionary"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(i18n_router, tags=["i18n"])
api_router.include_router(attendance_router, tags=["attendance"])
