import os
import tempfile
import shutil
import json
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.parser.gw2_log_parser import GW2LogParser
from src.scoring.scoring_engine import ScoringEngine
from src.database.db_manager import DBManager
from src.reports.exporter import export_report
from src.config import settings
from src.core.logger import Logger

logger = Logger(__name__)

router = APIRouter()

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "databases", "gw2_logs.db")


def ensure_db_exists():
    """确保数据库文件存在，如不存在则初始化"""
    if not os.path.exists(db_path):
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        DBManager(db_path)


def compute_file_hash(file_path: str) -> str:
    """
    计算文件的MD5哈希值，用于检测重复上传

    Args:
        file_path: 文件路径

    Returns:
        MD5哈希字符串
    """
    import hashlib
    hash_obj = hashlib.md5()
    with open(file_path, "rb") as f:
        hash_obj.update(f.read())
    return hash_obj.hexdigest()


def _save_parsed_data(db: DBManager, parsed_data: Dict[str, Any], file_hash: str, log_id: str) -> List[Dict[str, Any]]:
    """
    保存解析后的数据到数据库

    Args:
        db: 数据库管理器实例
        parsed_data: 解析后的日志数据
        file_hash: 文件哈希值
        log_id: 日志唯一标识

    Returns:
        评分结果列表
    """
    db.save_combat_log(
        log_id,
        parsed_data['mode'],
        parsed_data['encounter_name'],
        parsed_data.get('date', ''),
        parsed_data['duration'],
        file_hash,
        parsed_data.get('recorded_by', '')
    )

    for p in parsed_data['players']:
        db.save_player(
            p['name'],
            p['profession'],
            p.get('role', ''),
            p.get('account', '')
        )

    engine = ScoringEngine()
    scores = engine.calculate_scores(parsed_data)

    for s in scores:
        db.save_score(
            log_id,
            s['player_name'],
            s['scores'].get('dps', 0),
            s['scores'].get('cc', 0),
            s['scores'].get('survival', 0),
            0,
            s['total_score'],
            json.dumps(s['details'])
        )

    return scores


@router.post("/upload", summary="上传日志文件", description="上传GW2日志文件(JSON/EVTC/ZEVTC格式)，自动解析并计算评分")
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
        ensure_db_exists()

        temp_dir = tempfile.mkdtemp()
        try:
            file_path = os.path.join(temp_dir, file.filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            file_hash = compute_file_hash(file_path)

            db = DBManager(db_path)
            existing_log = db.get_log_by_hash(file_hash)
            is_update = False

            if existing_log:
                logger.info("File with same content already exists")
                is_update = True

            parser = GW2LogParser()
            parsed_data = parser.parse_file(file_path)

            if not parsed_data:
                raise HTTPException(status_code=400, detail="Failed to parse log file")

            if existing_log:
                logger.info("File with same content already exists, skipping")
                return {
                    "status": "success",
                    "message": "文件已存在，跳过处理",
                    "encounter": parsed_data['encounter_name'],
                    "player_count": len(parsed_data['players']),
                    "file": os.path.basename(file_path),
                    "is_update": True,
                    "log_id": existing_log['log_id']
                }
            else:
                log_id = str(uuid.uuid4())

            scores = _save_parsed_data(db, parsed_data, file_hash, log_id)

            logger.info("Processing successful")

            message = "已替换今日数据" if is_update else "上传成功"

            return {
                "status": "success",
                "message": message,
                "encounter": parsed_data['encounter_name'],
                "player_count": len(scores),
                "file": os.path.basename(file_path),
                "is_update": is_update,
                "log_id": log_id
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing log: {e}")
            raise HTTPException(status_code=500, detail=f"日志处理失败: {type(e).__name__}")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {type(e).__name__}")


@router.get("/logs", summary="获取所有日志", description="获取系统中所有已上传的战斗日志列表")
async def get_all_logs():
    """
    获取所有战斗日志记录

    Returns:
        包含所有日志记录的列表，按日期降序排列
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        logs = db.get_all_logs()

        return {
            "status": "success",
            "data": logs
        }
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=f"获取日志列表失败: {type(e).__name__}")


@router.get("/scores", summary="获取评分数据", description="获取所有评分记录或指定日志的评分")
async def get_scores(log_id: Optional[str] = Query(None, description="可选的日志ID，指定则返回该日志的评分")):
    """
    获取战斗评分数据

    支持两种模式:
    - 不指定log_id: 返回所有评分记录
    - 指定log_id: 返回该特定日志的所有评分

    包含玩家信息、职业、角色定位及各项得分
    """
    try:
        ensure_db_exists()
        import sqlite3

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if log_id:
                cursor.execute('''
                    SELECT cs.*, cl.date, cl.encounter_name, cl.mode,
                           p.profession, p.role, p.account
                    FROM combat_scores cs
                    LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                    LEFT JOIN players p ON cs.player_name = p.name
                    WHERE cs.log_id = ?
                    ORDER BY cs.total_score DESC
                ''', (log_id,))
            else:
                cursor.execute('''
                    SELECT cs.*, cl.date, cl.encounter_name, cl.mode,
                           p.profession, p.role, p.account
                    FROM combat_scores cs
                    LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                    LEFT JOIN players p ON cs.player_name = p.name
                    ORDER BY cs.total_score DESC
                ''')

            scores = [dict(row) for row in cursor.fetchall()]

        return {
            "status": "success",
            "data": scores
        }
    except Exception as e:
        logger.error(f"Failed to get scores: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分失败: {type(e).__name__}")


@router.get("/scores/{log_id}", summary="获取指定日志评分", description="获取特定日志ID的评分详情")
async def get_log_scores(log_id: str):
    """
    获取指定日志的评分详情

    Args:
        log_id: 日志唯一标识符

    Returns:
        该日志的所有玩家评分，按总分降序排列
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        scores = db.get_scores_by_log(log_id)

        return {
            "status": "success",
            "data": scores
        }
    except Exception as e:
        logger.error(f"Failed to get scores: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分失败: {type(e).__name__}")


@router.get("/history", summary="获取历史记录", description="获取战斗日志历史记录")
async def get_history(mode: Optional[str] = Query(None, description="可选的游戏模式过滤(PVE/WvW/PvP等)")):
    """
    获取战斗日志历史

    支持按游戏模式过滤，返回历史战斗记录列表
    """
    try:
        ensure_db_exists()
        import sqlite3

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM combat_logs"
            params = []

            if mode and mode != "all":
                query += " WHERE mode = ?"
                params.append(mode)

            query += " ORDER BY date DESC"

            cursor.execute(query, params)
            logs = [dict(row) for row in cursor.fetchall()]

            return {
                "status": "success",
                "data": logs
            }

    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {type(e).__name__}")


@router.post("/local_sync", summary="本地同步", description="执行本地数据同步操作")
async def local_sync():
    """
    执行本地数据同步

    用于前端获取最新数据状态
    """
    try:
        ensure_db_exists()
        return {
            "status": "success",
            "message": "Local sync complete"
        }
    except Exception as e:
        logger.error(f"Local sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"同步失败: {type(e).__name__}")


@router.get("/attendance", summary="获取出勤统计", description="获取所有玩家的出勤统计信息")
async def get_attendance():
    """
    获取所有玩家的出勤统计

    统计信息包括:
    - 出勤次数
    - 最后出勤日期
    - 玩家职业和角色定位
    """
    try:
        import sqlite3

        if not os.path.exists(db_path):
            return []

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    p.name,
                    p.account,
                    p.profession,
                    p.role,
                    COUNT(cs.id) as attendance_count,
                    MAX(cl.date) as last_attendance
                FROM players p
                LEFT JOIN combat_scores cs ON p.name = cs.player_name
                LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                GROUP BY p.name
                ORDER BY attendance_count DESC
            ''')

            attendance = [dict(row) for row in cursor.fetchall()]
            return attendance

    except Exception as e:
        logger.error(f"Failed to get attendance: {e}")
        raise HTTPException(status_code=500, detail=f"获取出勤统计失败: {type(e).__name__}")


@router.get("/attendance/{player_name}", summary="获取玩家出勤详情", description="获取特定玩家的详细出勤记录")
async def get_attendance_detail(player_name: str):
    """
    获取指定玩家的详细出勤记录

    Args:
        player_name: 玩家名称

    Returns:
    - 玩家基本信息
    - 使用过的所有角色信息
    - 出勤日期列表
    - 详细的战斗评分记录
    """
    try:
        import sqlite3

        if not os.path.exists(db_path):
            return {}

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM players WHERE name = ?
            ''', (player_name,))
            player_info = cursor.fetchone()

            cursor.execute('''
                SELECT DISTINCT name, profession, role FROM players WHERE account = ?
            ''', (player_info['account'] if player_info else player_name,))
            roles = [dict(row) for row in cursor.fetchall()]

            cursor.execute('''
                SELECT DISTINCT cl.date, cl.log_id, cl.encounter_name, cl.mode
                FROM combat_scores cs
                LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                WHERE cs.player_name = ?
                ORDER BY cl.date DESC
            ''', (player_name,))
            attendance_dates = [dict(row) for row in cursor.fetchall()]

            cursor.execute('''
                SELECT cs.*, cl.encounter_name, cl.mode, cl.date
                FROM combat_scores cs
                LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                WHERE cs.player_name = ?
                ORDER BY cl.date DESC
            ''', (player_name,))
            attendance_details = [dict(row) for row in cursor.fetchall()]

            return {
                "player_info": dict(player_info) if player_info else {},
                "roles": roles,
                "attendance_dates": attendance_dates,
                "attendance_details": attendance_details
            }

    except Exception as e:
        logger.error(f"Failed to get attendance detail: {e}")
        raise HTTPException(status_code=500, detail=f"获取出勤详情失败: {type(e).__name__}")


@router.get("/export", summary="导出日志数据", description="导出所有评分数据为CSV文件")
async def export_logs():
    """
    导出所有评分数据

    生成包含以下信息的CSV文件:
    - 日期、战斗名称、游戏模式
    - 玩家名称、职业、角色定位
    - DPS得分、CC得分、生存得分、辅助得分、总分
    """
    try:
        ensure_db_exists()

        temp_dir = tempfile.mkdtemp()
        try:
            csv_path = os.path.join(temp_dir, "gw2_log_scores.csv")
            export_report(db_path, csv_path)

            from fastapi.responses import FileResponse
            return FileResponse(csv_path, filename="gw2_log_scores.csv")

        finally:
            pass

    except Exception as e:
        logger.error(f"Failed to export logs: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {type(e).__name__}")


@router.post("/clear/all", summary="清空所有数据", description="清空数据库中的所有数据，可选择是否备份")
async def clear_all_data(backup: bool = Query(True, description="是否在清除前备份数据库")):
    """
    清空所有战斗数据和评分记录

    Warning:
        此操作不可逆，建议开启备份

    Args:
        backup: 是否在清除前创建数据库备份
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        success = db.clear_all_data(backup=backup)

        if success:
            return {
                "status": "success",
                "message": "所有数据已清空"
            }
        else:
            raise HTTPException(status_code=500, detail="清空数据失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear all data: {e}")
        raise HTTPException(status_code=500, detail=f"清空数据失败: {type(e).__name__}")


@router.post("/clear/today", summary="清空当日数据", description="清空当日的所有战斗数据")
async def clear_today_data(backup: bool = Query(True, description="是否在清除前备份数据库")):
    """
    清空当日的战斗数据和评分记录

    用于重置当天数据或重新统计

    Args:
        backup: 是否在清除前创建数据库备份
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        success = db.clear_today_data(backup=backup)

        if success:
            return {
                "status": "success",
                "message": "当日数据已清空"
            }
        else:
            raise HTTPException(status_code=500, detail="清空当日数据失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear today data: {e}")
        raise HTTPException(status_code=500, detail=f"清空数据失败: {type(e).__name__}")


class ClearDataRequest(BaseModel):
    type: str

@router.post("/clear_data", summary="清除数据", description="根据类型清除数据，支持清除当天数据或全部数据")
async def clear_data(request: ClearDataRequest):
    """
    根据类型清除数据

    Args:
        request: 包含清除类型的请求体
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        
        type = request.type
        if type == 'today':
            success = db.clear_today_data(backup=False)
            message = "当日数据已清空"
        elif type == 'all':
            success = db.clear_all_data(backup=False)
            message = "全部数据已清空"
        else:
            raise HTTPException(status_code=400, detail="无效的清除类型，支持的类型：'today' 或 'all'")

        if success:
            return {
                "status": "success",
                "message": message
            }
        else:
            raise HTTPException(status_code=500, detail="清空数据失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear data: {e}")
        raise HTTPException(status_code=500, detail=f"清空数据失败: {type(e).__name__}")