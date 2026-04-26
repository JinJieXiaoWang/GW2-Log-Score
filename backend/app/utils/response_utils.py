#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
响应处理工具

提供API响应相关的通用功能
"""

from typing import Any, Dict, Optional, List
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def create_success_response(
    data: Any = None, message: str = "操作成功"
) -> Dict[str, Any]:
    """
    创建成功响应

    Args:
        data: 响应数据
        message: 响应消息

    Returns:
        成功响应字典
    """
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return response


def create_error_response(error: str, message: str = "操作失败") -> Dict[str, Any]:
    """
    创建错误响应

    Args:
        error: 错误信息
        message: 响应消息

    Returns:
        错误响应字典
    """
    return {"status": "error", "message": message, "error": error}


def create_paginated_response(
    items: List[Any], total: int, page: int, page_size: int, message: str = "操作成功"
) -> Dict[str, Any]:
    """
    创建分页响应

    Args:
        items: 分页数据项
        total: 总数据量
        page: 当前页码
        page_size: 每页大小
        message: 响应消息

    Returns:
        分页响应字典
    """
    total_pages = (total + page_size - 1) // page_size

    return {
        "status": "success",
        "message": message,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            },
        },
    }


def raise_http_exception(
    status_code: int, detail: str, headers: Optional[Dict[str, str]] = None
) -> None:
    """
    抛出HTTP异常

    Args:
        status_code: HTTP状态码
        detail: 异常详情
        headers: 响应头
    """
    raise HTTPException(status_code=status_code, detail=detail, headers=headers)


def create_json_response(
    content: Dict[str, Any],
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """
    创建JSON响应

    Args:
        content: 响应内容
        status_code: HTTP状态码
        headers: 响应头

    Returns:
        JSONResponse对象
    """
    return JSONResponse(content=content, status_code=status_code, headers=headers)
