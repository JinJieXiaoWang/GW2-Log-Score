#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际化相关API路由
"""

from fastapi import APIRouter, HTTPException, Path
from app.core.i18n import i18n
from app.core.logger import Logger

router = APIRouter()
logger = Logger(__name__)


@router.get("/i18n/{locale}", summary="获取国际化翻译", description="获取指定语言的翻译数据")
async def get_i18n(locale: str = Path(..., description="语言区域，如zh-CN, en-US等")):
    """
    获取指定语言的翻译数据

    Args:
        locale: 语言区域，如zh-CN, en-US等

    Returns:
        翻译数据
    """
    try:
        # 检查语言是否存在
        if locale not in i18n.translations:
            # 如果不存在，返回默认语言
            locale = i18n.default_locale

        return {"status": "success", "data": i18n.translations.get(locale, {})}
    except Exception as e:
        logger.error(f"Failed to get i18n data: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取国际化数据失败: {type(e).__name__}"
        )


