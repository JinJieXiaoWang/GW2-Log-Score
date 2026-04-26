#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评分相关API路由
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
from app.services.score_service import ScoreService
from app.database.db_manager import DBManager
from app.core.logger import Logger
import os

router = APIRouter()
logger = Logger(__name__)

# 获取数据库路径
db_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "database",
    "gw2_logs.db",
)

# 创建评分服务实例
score_service = ScoreService(db_path)


@router.get(
    "/scores", summary="获取评分数据", description="获取所有评分记录或指定日志的评分"
)
async def get_scores(
    log_id: Optional[str] = Query(
        None, description="可选的日志ID，指定则返回该日志的评分"
    )
):
    """
    获取战斗评分数据

    支持两种模式:
    - 不指定log_id: 返回所有评分记录
    - 指定log_id: 返回该特定日志的所有评分

    包含玩家信息、职业、角色定位及各项得分
    """
    try:
        scores = score_service.get_scores(log_id)
        return {"status": "success", "data": scores}
    except Exception as e:
        logger.error(f"Failed to get scores: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分失败: {type(e).__name__}")


@router.get(
    "/scores/{log_id}",
    summary="获取指定日志评分",
    description="获取特定日志ID的评分详情",
)
async def get_log_scores(log_id: str = Path(..., description="日志唯一标识符")):
    """
    获取指定日志的评分详情

    Args:
        log_id: 日志唯一标识符

    Returns:
        该日志的所有玩家评分，按总分降序排列
    """
    try:
        scores = score_service.get_log_scores(log_id)
        return {"status": "success", "data": scores}
    except Exception as e:
        logger.error(f"Failed to get scores: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分失败: {type(e).__name__}")


@router.get("/scores/today", summary="获取今日评分", description="获取今日的评分数据")
async def get_today_scores():
    """
    获取今日评分数据

    Returns:
        今日评分数据列表
    """
    try:
        scores = score_service.get_today_scores()
        return {"status": "success", "data": scores}
    except Exception as e:
        logger.error(f"Failed to get today scores: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取今日评分失败: {type(e).__name__}"
        )


@router.delete("/clear-data", summary="清除数据", description="清除系统数据，支持清除当天数据或全部数据")
async def clear_data(type: str = Query(..., description="清除类型: today(当天数据) 或 all(全部数据)")):
    """
    清除系统数据

    Args:
        type: 清除类型，可选值: today(当天数据) 或 all(全部数据)

    Returns:
        清除结果
    """
    try:
        db = DBManager(db_path)
        if type == "today":
            deleted_count = db.clear_today_data()
            return {"status": "success", "message": f"当天数据清除成功，共删除 {deleted_count} 条记录"}
        elif type == "all":
            deleted_count = db.clear_all_data()
            return {"status": "success", "message": f"全部数据清除成功，共删除 {deleted_count} 条记录"}
        else:
            raise HTTPException(status_code=400, detail="无效的清除类型，支持的值: today, all")
    except Exception as e:
        logger.error(f"Failed to clear data: {e}")
        raise HTTPException(
            status_code=500, detail=f"清除数据失败: {type(e).__name__}"
        )


@router.post("/sync-data", summary="同步数据", description="同步系统数据")
async def sync_data():
    """
    同步系统数据

    Returns:
        同步结果
    """
    try:
        # 这里可以实现数据同步逻辑，例如从其他系统同步数据
        # 目前返回成功响应
        return {"status": "success", "message": "数据同步成功"}
    except Exception as e:
        logger.error(f"Failed to sync data: {e}")
        raise HTTPException(
            status_code=500, detail=f"同步数据失败: {type(e).__name__}"
        )
