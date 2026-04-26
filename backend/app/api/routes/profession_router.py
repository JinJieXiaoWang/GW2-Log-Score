#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职业相关API路由
"""

from fastapi import APIRouter, HTTPException
from app.services.profession_service import ProfessionService
from app.core.logger import Logger

router = APIRouter()
logger = Logger(__name__)

# 创建职业服务实例
profession_service = ProfessionService()


@router.get(
    "/professions",
    summary="获取职业数据",
    description="获取所有职业信息，包括翻译和颜色",
)
async def get_professions():
    """
    获取职业数据

    Returns:
        职业数据，包括翻译和颜色配置
    """
    try:
        professions = profession_service.get_professions()
        colors = profession_service.get_profession_colors()
        role_types = profession_service.get_role_types()
        role_config = profession_service.get_role_config()
        default_roles = profession_service.get_profession_default_roles()

        return {
            "status": "success",
            "data": {
                "translations": professions,
                "colors": colors,
                "role_types": role_types,
                "role_config": role_config,
                "default_roles": default_roles,
            },
        }
    except Exception as e:
        logger.error(f"Failed to get professions: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取职业数据失败: {type(e).__name__}"
        )


@router.get(
    "/professions/full",
    summary="获取完整职业数据",
    description="获取完整的职业数据，包括所有相关信息",
)
async def get_professions_full():
    """
    获取完整职业数据

    Returns:
        完整的职业数据列表
    """
    try:
        data = profession_service.get_professions_full_data()
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to get full professions data: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取完整职业数据失败: {type(e).__name__}"
        )
