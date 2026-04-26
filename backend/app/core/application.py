#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI应用程序配置模块

负责应用程序初始化、中间件配置和路由注册
"""

import os
import sys
from typing import List

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import api_router
from app.core.logger import Logger

logger = Logger(__name__)


class CORSConfig:
    """
    CORS配置管理器
    根据环境自动配置跨域策略:
    - 开发环境: 允许所有来源或localhost
    - 生产环境: 仅允许配置的域名
    """

    DEV_ALLOW_ORIGINS = ["*"]
    DEV_ALLOW_METHODS = ["*"]
    DEV_ALLOW_HEADERS = ["*"]
    PROD_ALLOW_ORIGINS = []

    @classmethod
    def _get_cors_attr(cls, name, default=None):
        """统一访问CORS配置属性"""
        return default

    @classmethod
    def get_origins(cls) -> List[str]:
        """获取允许的来源列表"""
        env_origins = os.getenv("CORS_ORIGINS")
        if env_origins:
            origins = [origin.strip() for origin in env_origins.split(",")]
            logger.info(f"CORS origins from environment: {origins}")
            return origins

        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            logger.warning(
                "Production environment detected but no CORS_ORIGINS configured. "
                "Using restrictive defaults."
            )
            return cls.PROD_ALLOW_ORIGINS

        logger.info("Using development CORS settings (allow all origins)")
        return cls.DEV_ALLOW_ORIGINS

    @classmethod
    def get_methods(cls) -> List[str]:
        """获取允许的HTTP方法列表"""
        return cls.DEV_ALLOW_METHODS

    @classmethod
    def get_headers(cls) -> List[str]:
        """获取允许的请求头列表"""
        return cls.DEV_ALLOW_HEADERS

    @classmethod
    def get_expose_headers(cls) -> List[str]:
        """获取暴露给前端的响应头列表"""
        return []

    @classmethod
    def get_max_age(cls) -> int:
        """获取预检请求缓存时间"""
        return 3600

    @classmethod
    def allow_credentials(cls) -> bool:
        """是否允许携带认证信息"""
        return True


class Application:
    """
    FastAPI应用程序类
    负责应用程序的初始化和配置
    """

    def __init__(self):
        self.app = FastAPI(
            title="GW2 Log Score API",
            description="""
Guild Wars 2 战斗日志评分系统 API

## 功能特性
- 上传并解析战斗日志文件(JSON/EVTC/ZEVTC格式)
- 自动计算玩家评分 (支持PVE/WvW模式)
- 导出评分报告

## 支持的日志格式
- JSON: EI导出的data.json
- EVTC: GW2原生日志格式
- ZEVTC/ZETVC: ZIP压缩的日志格式
            """,
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc",
            openapi_url="/api/openapi.json",
        )

        self._configure_cors()
        self._register_routers()
        self._register_exception_handlers()
        self._register_startup_events()

        logger.info("Application initialized successfully")

    def _configure_cors(self) -> None:
        """
        配置CORS中间件
        采用标准后端API实践:
        - 从配置或环境变量读取允许的来源
        - 支持开发/生产环境切换
        - 提供合理的默认值
        """
        origins = CORSConfig.get_origins()
        methods = CORSConfig.get_methods()
        headers = CORSConfig.get_headers()
        expose_headers = CORSConfig.get_expose_headers()
        max_age = CORSConfig.get_max_age()
        allow_credentials = CORSConfig.allow_credentials()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=allow_credentials,
            allow_methods=methods,
            allow_headers=headers,
            expose_headers=expose_headers,
            max_age=max_age,
        )

        logger.info(
            f"CORS configured - Origins: {origins}, "
            f"Methods: {methods}, Credentials: {allow_credentials}"
        )

    def _register_routers(self) -> None:
        """注册API路由"""
        self.app.include_router(api_router, prefix="/api")
        logger.info("API routes registered at /api")

    def _register_startup_events(self) -> None:
        """注册应用启动事件"""

        @self.app.on_event("startup")
        async def startup_event():
            logger.info("Running startup tasks...")
            try:
                from app.database.db_manager import DBManager
                from app.database.dict_init import DictionaryDataInitializer

                db_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "database",
                    "gw2_logs.db",
                )
                db = DBManager(db_path)
                initializer = DictionaryDataInitializer(db)
                results = initializer.initialize_all()

                total_created = sum(r["created"] for r in results.values())
                total_skipped = sum(r["skipped"] for r in results.values())
                logger.info(
                    f"Dictionary data initialization completed: "
                    f"{total_created} created, {total_skipped} skipped"
                )
            except Exception as e:
                logger.error(f"Failed to initialize dictionary data: {e}")

    def _register_exception_handlers(self) -> None:
        """注册全局异常处理器"""

        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "detail": (
                        str(exc) if os.getenv("ENVIRONMENT") != "production" else None
                    ),
                },
            )

    def get_app(self) -> FastAPI:
        """
        获取FastAPI应用实例

        Returns:
            配置完成的FastAPI应用
        """
        return self.app


# 创建应用实例
application = Application()
app = application.get_app()
