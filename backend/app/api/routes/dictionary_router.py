#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典相关API路由
"""

from fastapi import APIRouter, HTTPException, Query, Path, Response
from app.services.dictionary_service import DictionaryService
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

# 创建字典服务实例
dictionary_service = DictionaryService(db_path)


@router.get("/dict", summary="获取字典数据", description="获取指定类型的字典数据")
async def get_dict(
    dict_type: str = Query(..., description="字典类型"),
    format: str = Query(
        "datas", description="返回格式: datas(数据列表) 或 options(选项列表)"
    ),
):
    """
    获取字典数据

    Args:
        dict_type: 字典类型
        format: 返回格式，可选值：datas(数据列表) 或 options(选项列表)

    Returns:
        字典数据
    """
    try:
        if format == "options":
            data = dictionary_service.get_dict_options(dict_type)
        else:
            data = dictionary_service.get_dict_datas(dict_type)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to get dict: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典数据失败: {type(e).__name__}"
        )


@router.get(
    "/dict/labels", summary="获取字典标签", description="获取指定类型的所有字典标签"
)
async def get_dict_labels(dict_type: str = Query(..., description="字典类型")):
    """
    获取字典标签

    Args:
        dict_type: 字典类型

    Returns:
        字典标签列表
    """
    try:
        labels = dictionary_service.get_dict_labels(dict_type)
        return {"status": "success", "data": labels}
    except Exception as e:
        logger.error(f"Failed to get dict labels: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典标签失败: {type(e).__name__}"
        )


@router.get(
    "/dict/values", summary="获取字典值", description="获取指定类型的所有字典值"
)
async def get_dict_values(dict_type: str = Query(..., description="字典类型")):
    """
    获取字典值

    Args:
        dict_type: 字典类型

    Returns:
        字典值列表
    """
    try:
        values = dictionary_service.get_dict_values(dict_type)
        return {"status": "success", "data": values}
    except Exception as e:
        logger.error(f"Failed to get dict values: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典值失败: {type(e).__name__}"
        )


@router.get("/dict/categories", summary="获取字典分类", description="获取所有字典分类")
async def get_dict_categories():
    """
    获取所有字典分类

    Returns:
        字典分类列表
    """
    try:
        categories = dictionary_service.get_dict_categories()
        return {"status": "success", "data": categories}
    except Exception as e:
        logger.error(f"Failed to get dict categories: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典分类失败: {type(e).__name__}"
        )


@router.get(
    "/dict/category/{category_code}",
    summary="获取分组字典",
    description="获取指定分组下的字典",
)
async def get_dict_by_category(category_code: str = Path(..., description="分类编码")):
    """
    获取分组下的字典

    Args:
        category_code: 分类编码

    Returns:
        字典列表
    """
    try:
        data = dictionary_service.get_dict_by_category(category_code)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to get dict by category: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取分组字典失败: {type(e).__name__}"
        )


@router.get(
    "/dict/detail/{dict_id}", summary="获取字典详情", description="获取指定字典ID的详情"
)
async def get_dict_detail(dict_id: int = Path(..., description="字典ID")):
    """
    获取字典项详情

    Args:
        dict_id: 字典ID

    Returns:
        字典项详情
    """
    try:
        data = dictionary_service.get_dict_detail(dict_id)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to get dict detail: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典详情失败: {type(e).__name__}"
        )


@router.get(
    "/dict/code", summary="通过编码获取字典", description="通过分组编码和字典值获取字典"
)
async def get_dict_by_code(
    category_code: str = Query(..., description="分类编码"),
    dict_value: str = Query(..., description="字典值"),
):
    """
    通过分组编码和字典值获取字典

    Args:
        category_code: 分类编码
        dict_value: 字典值

    Returns:
        字典详情
    """
    try:
        data = dictionary_service.get_dict_by_code(category_code, dict_value)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to get dict by code: {e}")
        raise HTTPException(
            status_code=500, detail=f"通过编码获取字典失败: {type(e).__name__}"
        )


@router.get("/dict/groups", summary="获取字典分组", description="获取所有字典分组")
async def get_dict_groups(response: Response):
    """
    获取所有字典分组

    Returns:
        字典分组列表
    """
    try:
        # 设置响应编码为UTF-8
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        # 这里可以返回字典分类作为分组
        groups = dictionary_service.get_dict_categories()
        return {"status": "success", "data": groups}
    except Exception as e:
        logger.error(f"Failed to get dict groups: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典分组失败: {type(e).__name__}"
        )


@router.get("/dict/status", summary="获取字典状态", description="获取字典服务状态")
async def get_dict_status():
    """
    获取字典服务状态

    Returns:
        字典服务状态
    """
    try:
        # 返回字典服务状态
        status = {
            "initialized": True,
            "categories_count": len(dictionary_service.get_dict_categories()),
            "message": "Dictionary service is running"
        }
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Failed to get dict status: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典状态失败: {type(e).__name__}"
        )


@router.get("/dict/utils/datas/{dict_type}", summary="获取字典数据（兼容前端路径）", description="获取指定类型的字典数据")
async def get_dict_utils_datas(dict_type: str = Path(..., description="字典类型")):
    """
    获取指定类型的字典数据（兼容前端路径）

    Args:
        dict_type: 字典类型

    Returns:
        字典数据
    """
    try:
        data = dictionary_service.get_dict_datas(dict_type)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to get dict utils datas: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典数据失败: {type(e).__name__}"
        )


@router.post("/dict/groups", summary="创建字典分组", description="创建新的字典分组")
async def create_dict_group(data: dict):
    """
    创建字典分组

    Args:
        data: 分组数据，包含dict_name, dict_type, remark, status, sort_order

    Returns:
        创建的分组信息
    """
    try:
        result = dictionary_service.create_dict_group(data)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to create dict group: {e}")
        raise HTTPException(
            status_code=500, detail=f"创建字典分组失败: {type(e).__name__}"
        )


@router.put("/dict/groups/{dict_id}", summary="更新字典分组", description="更新指定的字典分组")
async def update_dict_group(dict_id: int = Path(..., description="分组ID"), data: dict = None):
    """
    更新字典分组

    Args:
        dict_id: 分组ID
        data: 分组数据，包含dict_name, remark, status, sort_order

    Returns:
        更新后的分组信息
    """
    try:
        result = dictionary_service.update_dict_group(dict_id, data)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to update dict group: {e}")
        raise HTTPException(
            status_code=500, detail=f"更新字典分组失败: {type(e).__name__}"
        )


@router.delete("/dict/groups/{dict_id}", summary="删除字典分组", description="删除指定的字典分组")
async def delete_dict_group(dict_id: int = Path(..., description="分组ID")):
    """
    删除字典分组

    Args:
        dict_id: 分组ID

    Returns:
        删除结果
    """
    try:
        result = dictionary_service.delete_dict_group(dict_id)
        return {"status": "success", "message": "分组删除成功"}
    except Exception as e:
        logger.error(f"Failed to delete dict group: {e}")
        raise HTTPException(
            status_code=500, detail=f"删除字典分组失败: {type(e).__name__}"
        )


@router.get("/dict/groups/{dict_type}/items", summary="获取分组下的字典项", description="获取指定分组下的字典项")
async def get_dict_items_by_group(
    dict_type: str = Path(..., description="分组类型"),
    include_disabled: bool = Query(False, description="是否包含禁用项")
):
    """
    获取分组下的字典项

    Args:
        dict_type: 分组类型
        include_disabled: 是否包含禁用项

    Returns:
        字典项列表
    """
    try:
        data = dictionary_service.get_dict_items_by_group(dict_type, include_disabled)
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Failed to get dict items: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取字典项失败: {type(e).__name__}"
        )


@router.post("/dict/items", summary="创建字典项", description="创建新的字典项")
async def create_dict_item(data: dict):
    """
    创建字典项

    Args:
        data: 字典项数据，包含group_id, item_code, item_name, item_value, description, status, sort_order, color

    Returns:
        创建的字典项信息
    """
    try:
        result = dictionary_service.create_dict_item(data)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to create dict item: {e}")
        raise HTTPException(
            status_code=500, detail=f"创建字典项失败: {type(e).__name__}"
        )


@router.put("/dict/items/{dict_code}", summary="更新字典项", description="更新指定的字典项")
async def update_dict_item(dict_code: int = Path(..., description="字典项ID"), data: dict = None):
    """
    更新字典项

    Args:
        dict_code: 字典项ID
        data: 字典项数据，包含item_name, item_value, description, status, sort_order, color

    Returns:
        更新后的字典项信息
    """
    try:
        result = dictionary_service.update_dict_item(dict_code, data)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to update dict item: {e}")
        raise HTTPException(
            status_code=500, detail=f"更新字典项失败: {type(e).__name__}"
        )


@router.delete("/dict/items/{dict_code}", summary="删除字典项", description="删除指定的字典项")
async def delete_dict_item(dict_code: int = Path(..., description="字典项ID")):
    """
    删除字典项

    Args:
        dict_code: 字典项ID

    Returns:
        删除结果
    """
    try:
        result = dictionary_service.delete_dict_item(dict_code)
        return {"status": "success", "message": "项目删除成功"}
    except Exception as e:
        logger.error(f"Failed to delete dict item: {e}")
        raise HTTPException(
            status_code=500, detail=f"删除字典项失败: {type(e).__name__}"
        )


@router.post("/dict/initialize", summary="初始化字典数据", description="初始化系统字典数据")
async def initialize_dict_data(response: Response):
    """
    初始化字典数据

    Returns:
        初始化结果
    """
    try:
        # 设置响应编码为UTF-8
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        
        from app.database.dict_init import DictionaryDataInitializer
        from app.database.db_manager import DBManager
        
        # 创建数据库管理器实例
        db_manager = DBManager(db_path)
        # 创建字典数据初始化器
        initializer = DictionaryDataInitializer(db_manager)
        # 执行初始化
        results = initializer.initialize_all()
        
        # 计算创建和跳过的总数
        total_created = sum(v["created"] for v in results.values())
        total_skipped = sum(v["skipped"] for v in results.values())
        
        return {
            "status": "success", 
            "message": "字典数据初始化成功",
            "data": {
                "total_created": total_created,
                "total_skipped": total_skipped,
                "details": results
            }
        }
    except Exception as e:
        logger.error(f"Failed to initialize dict data: {e}")
        raise HTTPException(
            status_code=500, detail=f"初始化字典数据失败: {type(e).__name__}"
        )


@router.post("/dict/reinitialize", summary="重新初始化字典数据", description="清空并重新初始化系统字典数据")
async def reinitialize_dict_data(response: Response, force: bool = False):
    """
    重新初始化字典数据

    Args:
        force: 是否强制初始化，跳过确认

    Returns:
        初始化结果
    """
    try:
        # 设置响应编码为UTF-8
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        
        from app.database.dict_init import DictionaryDataInitializer
        from app.database.db_manager import DBManager
        
        # 创建数据库管理器实例
        db_manager = DBManager(db_path)
        # 创建字典数据初始化器
        initializer = DictionaryDataInitializer(db_manager)
        # 执行重新初始化
        results = initializer.reinitialize_all(force=force)
        
        # 根据返回状态处理
        if results.get("status") == "confirm_required":
            return {
                "status": "confirm_required",
                "message": results.get("message"),
                "data": {
                    "data_exists": results.get("data_exists")
                }
            }
        elif results.get("status") == "error":
            raise HTTPException(
                status_code=500, detail=results.get("message")
            )
        
        # 计算创建和跳过的总数
        total_created = sum(v["created"] for v in results.values() if isinstance(v, dict) and "created" in v)
        total_skipped = sum(v["skipped"] for v in results.values() if isinstance(v, dict) and "skipped" in v)
        
        return {
            "status": "success", 
            "message": results.get("message", "字典数据重新初始化成功"),
            "data": {
                "total_created": total_created,
                "total_skipped": total_skipped,
                "details": {k: v for k, v in results.items() if isinstance(v, dict) and ("created" in v or "skipped" in v)}
            }
        }
    except Exception as e:
        logger.error(f"Failed to reinitialize dict data: {e}")
        raise HTTPException(
            status_code=500, detail=f"重新初始化字典数据失败: {type(e).__name__}"
        )


