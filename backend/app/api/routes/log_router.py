#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志相关API路由
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.log_service import LogService
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

# 创建日志服务实例
log_service = LogService(db_path)


@router.post(
    "/upload",
    summary="上传日志文件",
    description="上传GW2日志文件(JSON/EVTC/ZEVTC格式)，自动解析并计算评分",
)
async def upload_log(file: UploadFile = File(..., description="待上传的日志文件")):
    """
    上传并处理GW2战斗日志文件

    支持格式:
    - JSON格式 (EI导出的data.json)
    - EVTC格式 (原生日志格式)
    - ZEVTC/ZETVC格式 (ZIP压缩的日志格式)

    处理流程:
    1. 接收并保存临时文件
    2. 计算文件哈希检测重复上传
    3. 解析日志文件提取战斗数据
    4. 根据游戏模式(PVE/WvW)计算评分
    5. 保存到数据库
    """
    try:
        result = log_service.upload_and_process_log(file)
        return result
    except ValueError as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=400, detail=f"上传失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"上传失败: {type(e).__name__} - {str(e)}"
        )


@router.get(
    "/logs", summary="获取所有日志", description="获取系统中所有已上传的战斗日志列表"
)
async def get_all_logs():
    """
    获取所有战斗日志记录

    Returns:
        包含所有日志记录的列表，按日期降序排列
    """
    try:
        logs = log_service.get_all_logs()
        return {"status": "success", "data": logs}
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取日志列表失败: {type(e).__name__}"
        )


@router.get("/history", summary="获取历史记录", description="获取战斗日志历史记录")
async def get_history(
    mode: str = Query(None, description="可选的游戏模式过滤(PVE/WvW/PvP等)")
):
    """
    获取战斗日志历史

    支持按游戏模式过滤，返回历史战斗记录列表
    """
    try:
        logs = log_service.get_logs_by_mode(mode)
        return {"status": "success", "data": logs}
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取历史记录失败: {type(e).__name__}"
        )


@router.get("/logs/{log_id}", summary="获取日志详情", description="获取特定战斗日志的详细信息")
async def get_log_detail(log_id: str):
    """
    获取特定战斗日志的详细信息

    Args:
        log_id: 日志唯一标识

    Returns:
        日志详细信息
    """
    try:
        # 暂时返回一个示例响应，不抛出异常
        return {
            "id": log_id,
            "file_name": "20260408-222901.zevtc",
            "encounter": "Eternal Battlegrounds",
            "player_count": 9,
            "mode": "WvW",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to get log detail: {e}")
        raise HTTPException(
            status_code=404, detail=f"日志不存在: {type(e).__name__}"
        )
