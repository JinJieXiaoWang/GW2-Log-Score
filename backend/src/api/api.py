import os
import tempfile
import shutil
import json
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Path
from pydantic import BaseModel
from parser.gw2_log_parser import GW2LogParser
from scoring.scoring_engine import ScoringEngine
from database.db_manager import DBManager
from reports.exporter import export_report
from config import (
    PROFESSIONS,
    PROFESSION_COLORS,
    ROLE_CONFIG,
    PROF_ROLES,
    PROFESSIONS_FULL_DATA,
)
from config.config_loader import ConfigLoader
from core.logger import Logger
from utils.dict_utils import (
    get_dict_label,
    get_dict_value,
    get_dict_datas,
    get_dict_options,
    get_profession_chinese_name,
    get_specialization_chinese_name,
    get_dict_values,
    get_dict_labels,
    clear_dict_cache,
    remove_dict_cache
)

logger = Logger(__name__)
config_loader = ConfigLoader()

router = APIRouter()

db_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "gw2_logs.db",
)


def ensure_db_exists():
    """确保数据库文件存在，如不存在则初始化"""
    if not os.path.exists(db_path):
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        DBManager(db_path)


def compute_file_hash(file_path: str) -> str:
    """
    计算文件的MD5哈希值，用于检测重复上�?

    Args:
        file_path: 文件路径

    Returns:
        MD5哈希字符�?
    """
    import hashlib

    hash_obj = hashlib.md5()
    with open(file_path, "rb") as f:
        hash_obj.update(f.read())
    return hash_obj.hexdigest()


def _save_parsed_data(
    db: DBManager, parsed_data: Dict[str, Any], file_hash: str, log_id: str, filename: str
) -> List[Dict[str, Any]]:
    """
    保存解析后的数据到数据库

    Args:
        db: 数据库管理器实例
        parsed_data: 解析后的日志数据
        file_hash: 文件哈希�?
        log_id: 日志唯一标识

    Returns:
        评分结果列表
    """
    db.save_combat_log(
        log_id,
        parsed_data["mode"],
        parsed_data["encounter_name"],
        parsed_data.get("date", ""),
        parsed_data["duration"],
        file_hash,
        parsed_data.get("recorded_by", ""),
    )

    # 保存文件指纹
    db.save_file_fingerprint(filename, file_hash, log_id)

    for p in parsed_data["players"]:
        db.save_player(
            p["name"], p["profession"], p.get("role", ""), p.get("account", "")
        )

    engine = ScoringEngine()
    scores = engine.calculate_scores(parsed_data)

    for s in scores:
        # 兼容新旧数据格式
        if "scores" in s and isinstance(s["scores"], dict):
            # 新格式：保存完整的details（包含scores, weights, raw_values等）
            full_details = {
                **s.get("details", {}),
                "scores": s.get("scores", {}),
                "weights": s.get("weights", {}),
                "raw_values": s.get("raw_values", {}),
                "display_name": s.get("display_name", ""),
                "profession": s.get("profession", ""),
                "specialization": s.get("specialization", ""),
                "role": s.get("role", ""),
            }
            
            # 保存到数据库
            db.save_score(
                log_id,
                s["player_name"],
                s["scores"].get("damage_per_second", s["scores"].get("dps", 0)),
                s["scores"].get("breakbar_damage", s["scores"].get("cc", 0)),
                s["scores"].get("survival_score", s["scores"].get("survival", 0)),
                0,
                s["total_score"],
                json.dumps(full_details),
            )
        else:
            # 旧格式兼�?
            db.save_score(
                log_id,
                s["player_name"],
                s["scores"].get("dps", 0),
                s["scores"].get("cc", 0),
                s["scores"].get("survival", 0),
                0,
                s["total_score"],
                json.dumps(s["details"]),
            )

    return scores


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
    - ZEVTC/ZETVC格式 (ZIP压缩的日志格�?

    处理流程:
    1. 接收并保存临时文�?
    2. 计算文件哈希检测重复上�?
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
                    "encounter": parsed_data["encounter_name"],
                    "player_count": len(parsed_data["players"]),
                    "file": os.path.basename(file_path),
                    "is_update": True,
                    "log_id": existing_log["log_id"],
                }
            else:
                log_id = str(uuid.uuid4())

            scores = _save_parsed_data(db, parsed_data, file_hash, log_id, file.filename)

            logger.info("Processing successful")

            message = "已替换今日数据" if is_update else "上传成功"

            return {
                "status": "success",
                "message": message,
                "encounter": parsed_data["encounter_name"],
                "player_count": len(scores),
                "file": os.path.basename(file_path),
                "is_update": is_update,
                "log_id": log_id,
            }
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            logger.error(f"Error processing log: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500, detail=f"日志处理失败: {type(e).__name__} - {str(e)}"
            )
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Upload failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"上传失败: {type(e).__name__} - {str(e)}")


@router.get(
    "/logs", summary="获取所有日志", description="获取系统中所有已上传的战斗日志列表"
)
async def get_all_logs():
    """
    获取所有战斗日志记�?

    Returns:
        包含所有日志记录的列表，按日期降序排列
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        logs = db.get_all_logs()

        return {"status": "success", "data": logs}
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取日志列表失败: {type(e).__name__}"
        )


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
    - 不指定log_id: 返回所有评分记�?
    - 指定log_id: 返回该特定日志的所有评�?

    包含玩家信息、职业、角色定位及各项得分
    """
    try:
        ensure_db_exists()
        import sqlite3

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if log_id:
                cursor.execute(
                    """
                    SELECT cs.*, cl.date, cl.encounter_name, cl.mode,
                           p.profession, p.role, p.account
                    FROM combat_scores cs
                    LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                    LEFT JOIN players p ON cs.player_name = p.name
                    WHERE cs.log_id = ?
                    ORDER BY cs.total_score DESC
                """,
                    (log_id,),
                )
            else:
                cursor.execute("""
                    SELECT cs.*, cl.date, cl.encounter_name, cl.mode,
                           p.profession, p.role, p.account
                    FROM combat_scores cs
                    LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                    LEFT JOIN players p ON cs.player_name = p.name
                    ORDER BY cs.total_score DESC
                """)

            scores = [dict(row) for row in cursor.fetchall()]
            
            # 处理details字段，提取新评分数据格式
            for score in scores:
                if score.get("details"):
                    try:
                        details = json.loads(score["details"])
                        score["details"] = details
                        
                        # 如果details中有新格式的评分数据，直接提升到顶层
                        if "scores" in details:
                            score["scores"] = details["scores"]
                        if "weights" in details:
                            score["weights"] = details["weights"]
                        if "raw_values" in details:
                            score["raw_values"] = details["raw_values"]
                        if "display_name" in details:
                            score["display_name"] = details["display_name"]
                        if "profession" in details and not score.get("profession"):
                            score["profession"] = details["profession"]
                        if "specialization" in details:
                            score["specialization"] = details["specialization"]
                        if "role" in details and not score.get("role"):
                            score["role"] = details["role"]
                    except (json.JSONDecodeError, TypeError):
                        pass

        return {"status": "success", "data": scores}
    except Exception as e:
        logger.error(f"Failed to get scores: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分失败: {type(e).__name__}")


@router.get(
    "/scores/{log_id}",
    summary="获取指定日志评分",
    description="获取特定日志ID的评分详情",
)
async def get_log_scores(log_id: str):
    """
    获取指定日志的评分详�?

    Args:
        log_id: 日志唯一标识�?

    Returns:
        该日志的所有玩家评分，按总分降序排列
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        scores = db.get_scores_by_log(log_id)

        return {"status": "success", "data": scores}
    except Exception as e:
        logger.error(f"Failed to get scores: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分失败: {type(e).__name__}")


@router.get("/history", summary="获取历史记录", description="获取战斗日志历史记录")
async def get_history(
    mode: Optional[str] = Query(None, description="可选的游戏模式过滤(PVE/WvW/PvP�?")
):
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

            return {"status": "success", "data": logs}

    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取历史记录失败: {type(e).__name__}"
        )


@router.post("/local_sync", summary="本地同步", description="执行本地数据同步操作")
async def local_sync():
    """
    执行本地数据同步

    用于前端获取最新数据状�?
    """
    try:
        ensure_db_exists()
        return {"status": "success", "message": "Local sync complete"}
    except Exception as e:
        logger.error(f"Local sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"同步失败: {type(e).__name__}")


@router.get(
    "/attendance", summary="获取出勤统计", description="获取所有玩家的出勤统计信息"
)
async def get_attendance():
    """
    获取所有玩家的出勤统计

    统计信息包括:
    - 出勤次数
    - 最后出勤日�?
    - 玩家职业和角色定�?
    """
    try:
        import sqlite3

        if not os.path.exists(db_path):
            return []

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
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
            """)

            attendance = [dict(row) for row in cursor.fetchall()]
            return attendance

    except Exception as e:
        logger.error(f"Failed to get attendance: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取出勤统计失败: {type(e).__name__}"
        )


@router.get(
    "/attendance/{player_name}",
    summary="获取玩家出勤详情",
    description="获取特定玩家的详细出勤记录",
)
async def get_attendance_detail(player_name: str):
    """
    获取指定玩家的详细出勤记�?

    Args:
        player_name: 玩家名称

    Returns:
    - 玩家基本信息
    - 使用过的所有角色信�?
    - 出勤日期列表
    - 详细的战斗评分记�?
    """
    try:
        import sqlite3

        if not os.path.exists(db_path):
            return {}

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM players WHERE name = ?
            """,
                (player_name,),
            )
            player_info = cursor.fetchone()

            cursor.execute(
                """
                SELECT DISTINCT name, profession, role FROM players WHERE account = ?
            """,
                (player_info["account"] if player_info else player_name,),
            )
            roles = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                """
                SELECT DISTINCT cl.date, cl.log_id, cl.encounter_name, cl.mode
                FROM combat_scores cs
                LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                WHERE cs.player_name = ?
                ORDER BY cl.date DESC
            """,
                (player_name,),
            )
            attendance_dates = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                """
                SELECT cs.*, cl.encounter_name, cl.mode, cl.date
                FROM combat_scores cs
                LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                WHERE cs.player_name = ?
                ORDER BY cl.date DESC
            """,
                (player_name,),
            )
            attendance_details = [dict(row) for row in cursor.fetchall()]

            return {
                "player_info": dict(player_info) if player_info else {},
                "roles": roles,
                "attendance_dates": attendance_dates,
                "attendance_details": attendance_details,
            }

    except Exception as e:
        logger.error(f"Failed to get attendance detail: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取出勤详情失败: {type(e).__name__}"
        )


@router.get("/export", summary="导出日志数据", description="导出所有评分数据为CSV文件")
async def export_logs():
    """
    导出所有评分数�?

    生成包含以下信息的CSV文件:
    - 日期、战斗名称、游戏模�?
    - 玩家名称、职业、角色定�?
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


@router.post(
    "/clear/all",
    summary="清空所有数据",
    description="清空数据库中的所有数据，可选择是否备份",
)
async def clear_all_data(
    backup: bool = Query(True, description="是否在清除前备份数据")
):
    """
    清空所有战斗数据和评分记录

    Warning:
        此操作不可逆，建议开启备�?

    Args:
        backup: 是否在清除前创建数据库备�?
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        success = db.clear_all_data(backup=backup)

        if success:
            return {"status": "success", "message": "所有数据已清空"}
        else:
            raise HTTPException(status_code=500, detail="清空数据失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear all data: {e}")
        raise HTTPException(status_code=500, detail=f"清空数据失败: {type(e).__name__}")


@router.post(
    "/clear/today", summary="清空当日数据", description="清空当日的所有战斗数据"
)
async def clear_today_data(
    backup: bool = Query(True, description="是否在清除前备份数据")
):
    """
    清空当日的战斗数据和评分记录

    用于重置当天数据或重新统�?

    Args:
        backup: 是否在清除前创建数据库备�?
    """
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        success = db.clear_today_data(backup=backup)

        if success:
            return {"status": "success", "message": "当日数据已清空"}
        else:
            raise HTTPException(status_code=500, detail="清空当日数据失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear today data: {e}")
        raise HTTPException(status_code=500, detail=f"清空数据失败: {type(e).__name__}")


class ClearDataRequest(BaseModel):
    type: str


@router.post(
    "/clear_data",
    summary="清除数据",
    description="根据类型清除数据，支持清除当天数据或全部数据",
)
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
        if type == "today":
            success = db.clear_today_data(backup=False)
            message = "当日数据已清空"
        elif type == "all":
            success = db.clear_all_data(backup=False)
            message = "全部数据已清空"
        else:
            raise HTTPException(
                status_code=400, detail="无效的清除类型，支持的类型：'today' 或 'all'"
            )

        if success:
            return {"status": "success", "message": message}
        else:
            raise HTTPException(status_code=500, detail="清空数据失败")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear data: {e}")
        raise HTTPException(status_code=500, detail=f"清空数据失败: {type(e).__name__}")


@router.get(
    "/professions",
    summary="获取职业信息",
    description="获取所有职业的完整信息，包括翻译、颜色、角色定位配置",
)
async def get_professions():
    """
    获取所有职业的完整信息

    Returns:
        包含职业翻译、颜色、角色类型、角色定位配置的完整数据
    """
    try:
        return {"status": "success", "data": PROFESSIONS_FULL_DATA}
    except Exception as e:
        logger.error(f"Failed to get professions: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取职业信息失败: {type(e).__name__}"
        )


@router.get(
    "/professions/translations",
    summary="获取职业翻译",
    description="获取职业名称的中文翻译映射",
)
async def get_profession_translations():
    """
    获取职业名称翻译映射

    Returns:
        职业英文名到中文的映射字�?
    """
    try:
        return {"status": "success", "data": PROFESSIONS}
    except Exception as e:
        logger.error(f"Failed to get profession translations: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取职业翻译失败: {type(e).__name__}"
        )


@router.get(
    "/professions/colors",
    summary="获取职业颜色",
    description="获取职业对应的显示颜色配置",
)
async def get_profession_colors():
    """
    获取职业显示颜色配置

    Returns:
        职业对应的Tailwind颜色�?
    """
    try:
        return {"status": "success", "data": PROFESSION_COLORS}
    except Exception as e:
        logger.error(f"Failed to get profession colors: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取职业颜色失败: {type(e).__name__}"
        )


@router.get(
    "/professions/roles",
    summary="获取角色定位",
    description="获取职业的角色定位配置，包括主副角色类型和描述",
)
async def get_profession_roles():
    """
    获取职业角色定位配置

    Returns:
        各职业精英特长的角色类型配置
    """
    try:
        return {"status": "success", "data": ROLE_CONFIG}
    except Exception as e:
        logger.error(f"Failed to get profession roles: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取角色定位失败: {type(e).__name__}"
        )


@router.get(
    "/professions/default-roles",
    summary="获取默认角色定位",
    description="获取职业的默认角色定位映射",
)
async def get_default_roles():
    """
    获取职业默认角色定位

    Returns:
        职业到默认角色类型的映射
    """
    try:
        return {"status": "success", "data": PROF_ROLES}
    except Exception as e:
        logger.error(f"Failed to get default roles: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取默认角色定位失败: {type(e).__name__}"
        )


@router.get(
    "/professions/{profession}/role",
    summary="获取职业特定精英特长的角色定位",
    description="获取指定职业和精英特长的角色定位信息",
)
async def get_profession_role_info(
    profession: str, specialization: str = Query(..., description="精英特长名称")
):
    """
    获取指定职业和精英特长的角色定位信息

    Args:
        profession: 职业名称 (�?Guardian, Warrior �?
        specialization: 精英特长名称 (�?core, Firebrand �?

    Returns:
        该职业精英特长的角色类型配置
    """
    try:
        role_info = config_loader.get_profession_role_info(profession, specialization)
        if role_info is None:
            raise HTTPException(
                status_code=404,
                detail=f"未找到职�?{profession} 的精英特�?{specialization}",
            )
        return {"status": "success", "data": role_info}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profession role info: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取角色定位失败: {type(e).__name__}"
        )


@router.get(
    "/i18n/{locale}",
    summary="获取国际化数据",
    description="获取指定语言的国际化翻译数据",
)
async def get_i18n_data(locale: str = Path(..., description="语言代码，如 zh-CN, en-US")):
    """
    获取国际化翻译数�?

    Args:
        locale: 语言代码，如 zh-CN, en-US

    Returns:
        该语言的翻译数据，包括职业名称�?
    """
    try:
        import os
        import json
        # 直接读取翻译文件
        # 使用绝对路径以确保找到文�?
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        resource_dir = os.path.join(base_dir, "resources", "i18n")
        filepath = os.path.join(resource_dir, f"{locale}.json")
        
        # 直接返回文件内容，以便调�?
        if not os.path.exists(filepath):
            return {"status": "success", "data": {"error": f"File not found: {filepath}"}}
        
        with open(filepath, "r", encoding="utf-8") as f:
            translations = json.load(f)
        
        # 直接返回所有翻译数�?
        return {"status": "success", "data": translations}
    except Exception as e:
        logger.error(f"Failed to get i18n data: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取国际化数据失�? {type(e).__name__}"
        )


@router.get(
    "/scoring/rules",
    summary="获取评分规则配置",
    description="获取当前系统中配置的评分规则，包括职业专精级别的详细规则",
)
async def get_scoring_rules():
    """
    获取评分规则配置

    Returns:
        评分规则完整配置
    """
    try:
        rules = config_loader.get_scoring_all_rules()
        return {
            "status": "success",
            "data": {
                "version": rules.get("version", "unknown"),
                "mode": rules.get("mode", "WvW"),
                "default_threshold": rules.get("default_threshold", 80),
                "profession_specialization_rules": rules.get("profession_specialization_rules", {}),
                "fallback_role_rules": rules.get("fallback_role_rules", {}),
                "dimension_definitions": rules.get("dimension_definitions", {}),
            }
        }
    except Exception as e:
        logger.error(f"Failed to get scoring rules: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取评分规则失败: {type(e).__name__}"
        )


@router.get(
    "/scoring/dimensions",
    summary="获取评分维度定义",
    description="获取所有评分维度的定义和计算方法",
)
async def get_scoring_dimensions():
    """
    获取评分维度定义

    Returns:
        评分维度定义列表
    """
    try:
        dimensions = config_loader.get_scoring_dimension_definitions()
        return {
            "status": "success",
            "data": dimensions
        }
    except Exception as e:
        logger.error(f"Failed to get scoring dimensions: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取评分维度失败: {type(e).__name__}"
        )


@router.get(
    "/scoring/threshold",
    summary="获取评分阈值",
    description="获取评分合格阈值",
)
async def get_scoring_threshold():
    """
    获取评分阈�?

    Returns:
        评分阈�?
    """
    try:
        threshold = config_loader.get_scoring_threshold()
        return {
            "status": "success",
            "data": {
                "threshold": threshold
            }
        }
    except Exception as e:
        logger.error(f"Failed to get scoring threshold: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取评分阈值失�? {type(e).__name__}"
        )


@router.put(
    "/scoring/rules",
    summary="更新评分规则",
    description="更新评分规则配置，支持版本控制和备份",
)
async def update_scoring_rules(
    rules_data: dict,
    user: Optional[str] = Query("system", description="操作用户")
):
    """
    更新评分规则配置

    Args:
        rules_data: 新的评分规则数据
        user: 操作用户�?

    Returns:
        操作结果
    """
    try:
        success = config_loader.save_scoring_rules(rules_data, user)
        if success:
            return {
                "status": "success",
                "message": "评分规则更新成功",
                "version": config_loader.get_scoring_rules_version()
            }
        else:
            raise HTTPException(status_code=500, detail="保存失败")
    except Exception as e:
        logger.error(f"Failed to update scoring rules: {e}")
        raise HTTPException(
            status_code=500, detail=f"更新评分规则失败: {type(e).__name__}"
        )


@router.get(
    "/scoring/rules/backups",
    summary="获取评分规则备份列表",
    description="获取所有历史评分规则备份",
)
async def get_scoring_rules_backups():
    """
    获取评分规则备份列表

    Returns:
        备份文件列表
    """
    try:
        backups = config_loader.get_scoring_rules_backups()
        return {
            "status": "success",
            "data": backups
        }
    except Exception as e:
        logger.error(f"Failed to get scoring rules backups: {e}")
        raise HTTPException(
            status_code=500, detail=f"获取备份列表失败: {type(e).__name__}"
        )


@router.post(
    "/scoring/rules/backups/{backup_filename}/restore",
    summary="恢复评分规则",
    description="从指定备份文件恢复评分规则",
)
async def restore_scoring_rules(
    backup_filename: str,
    user: Optional[str] = Query("system", description="操作用户")
):
    """
    恢复评分规则

    Args:
        backup_filename: 备份文件�?
        user: 操作用户�?

    Returns:
        操作结果
    """
    try:
        success = config_loader.restore_scoring_rules_from_backup(backup_filename)
        if success:
            # 获取恢复后的规则并保存一次，以添加新的版本记�?
            rules = config_loader.get_scoring_all_rules()
            config_loader.save_scoring_rules(rules, user)
            return {
                "status": "success",
                "message": "评分规则恢复成功",
                "version": config_loader.get_scoring_rules_version()
            }
        else:
            raise HTTPException(status_code=404, detail="备份文件不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restore scoring rules: {e}")
        raise HTTPException(
            status_code=500, detail=f"恢复评分规则失败: {type(e).__name__}"
        )


# ==================== 字典管理API ====================

class DictGroupCreate(BaseModel):
    group_code: str
    group_name: str
    description: Optional[str] = None
    sort_order: int = 0


class DictGroupUpdate(BaseModel):
    group_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
    sort_order: Optional[int] = None


class DictItemCreate(BaseModel):
    group_id: int
    item_code: str
    item_name: str
    item_value: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0
    color: Optional[str] = None


class DictItemUpdate(BaseModel):
    item_name: Optional[str] = None
    item_value: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
    sort_order: Optional[int] = None
    color: Optional[str] = None


# 字典分组管理 (使用新表结构)
@router.get(
    "/dict/groups",
    summary="获取所有字典分类",
    description="获取系统中所有字典分组列表",
)
async def get_all_dict_groups():
    """获取所有字典分�?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        types = db.get_all_dict_types()
        # 转换为前端期望的格式
        groups = []
        for t in types:
            groups.append({
                "id": t["dict_id"],
                "group_code": t["dict_type"],
                "group_name": t["dict_name"],
                "description": t["remark"],
                "status": t["status"],
                "sort_order": t["sort_order"]
            })
        return {"status": "success", "data": groups}
    except Exception as e:
        logger.error(f"Failed to get dict groups: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典分组失败: {type(e).__name__}")


@router.get(
    "/dict/groups/{group_id}",
    summary="获取字典分组详情",
    description="获取指定字典分组的详细信�?,
)
async def get_dict_group(group_id: int):
    """获取字典分组详情"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        type_data = db.get_dict_type(group_id)
        if not type_data:
            raise HTTPException(status_code=404, detail="字典分组不存在")
        # 转换为前端期望的格式
        group = {
            "id": type_data["dict_id"],
            "group_code": type_data["dict_type"],
            "group_name": type_data["dict_name"],
            "description": type_data["remark"],
            "status": type_data["status"],
            "sort_order": type_data["sort_order"]
        }
        return {"status": "success", "data": group}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dict group: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典分组失败: {type(e).__name__}")


@router.post(
    "/dict/groups",
    summary="创建字典分组",
    description="创建新的字典分组",
)
async def create_dict_group(data: DictGroupCreate):
    """创建字典分组"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        existing = db.get_dict_type_by_code(data.group_code)
        if existing:
            raise HTTPException(status_code=400, detail="分组编码已存�?)
        dict_id = db.add_dict_type(
            dict_name=data.group_name,
            dict_type=data.group_code,
            sort_order=data.sort_order,
            remark=data.description
        )
        return {"status": "success", "data": {"id": dict_id}, "message": "创建成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create dict group: {e}")
        raise HTTPException(status_code=500, detail=f"创建字典分组失败: {type(e).__name__}")


@router.put(
    "/dict/groups/{group_id}",
    summary="更新字典分组",
    description="更新指定字典分组的信�?,
)
async def update_dict_group(group_id: int, data: DictGroupUpdate):
    """更新字典分组"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        type_data = db.get_dict_type(group_id)
        if not type_data:
            raise HTTPException(status_code=404, detail="字典分组不存在")
        db.update_dict_type(
            dict_id=group_id,
            dict_name=data.group_name,
            status=data.status,
            sort_order=data.sort_order,
            remark=data.description
        )
        return {"status": "success", "message": "更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update dict group: {e}")
        raise HTTPException(status_code=500, detail=f"更新字典分组失败: {type(e).__name__}")


@router.delete(
    "/dict/groups/{group_id}",
    summary="删除字典分组",
    description="删除指定字典分组及其下所有字典项",
)
async def delete_dict_group(group_id: int):
    """删除字典分组"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        type_data = db.get_dict_type(group_id)
        if not type_data:
            raise HTTPException(status_code=404, detail="字典分组不存在")
        db.delete_dict_type(group_id)
        return {"status": "success", "message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dict group: {e}")
        raise HTTPException(status_code=500, detail=f"删除字典分组失败: {type(e).__name__}")


# 字典项管�?(使用新表结构)
@router.get(
    "/dict/groups/{group_id}/items",
    summary="获取分组下的字典�?,
    description="获取指定字典分组下的所有字典项",
)
async def get_dict_items_by_group(
    group_id: int,
    include_disabled: bool = Query(False, description="是否包含禁用的项")
):
    """获取分组下的字典""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        type_data = db.get_dict_type(group_id)
        if not type_data:
            raise HTTPException(status_code=404, detail="字典分组不存在")
        dict_type = type_data["dict_type"]
        items_data = db.get_dict_data_by_type(dict_type, include_disabled)
        # 转换为前端期望的格式
        items = []
        for item in items_data:
            items.append({
                "id": item["dict_code"],
                "group_id": group_id,
                "item_code": item["dict_value"],
                "item_name": item["dict_label"],
                "item_value": item.get("data_type", ""),
                "description": item["remark"],
                "status": item["status"],
                "sort_order": item["dict_sort"],
                "color": item.get("color")
            })
        return {"status": "success", "data": items}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dict items: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典项失�? {type(e).__name__}")


@router.get(
    "/dict/items/{item_id}",
    summary="获取字典项详情",
    description="获取指定字典项的详细信息",
)
async def get_dict_item(item_id: int):
    """获取字典项详�d?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        item_data = db.get_dict_data(item_id)
        if not item_data:
            raise HTTPException(status_code=404, detail="字典项不存在")
        # 查找对应的group_id
        type_data = db.get_dict_type_by_code(item_data["dict_type"])
        group_id = type_data["dict_id"] if type_data else 0
        # 转换为前端期望的格式
        item = {
            "id": item_data["dict_code"],
            "group_id": group_id,
            "item_code": item_data["dict_value"],
            "item_name": item_data["dict_label"],
            "item_value": item_data.get("data_type", ""),
            "description": item_data["remark"],
            "status": item_data["status"],
            "sort_order": item_data["dict_sort"],
            "color": item_data.get("color")
        }
        return {"status": "success", "data": item}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dict item: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典项失�? {type(e).__name__}")


@router.get(
    "/dict/by-code/{group_code}",
    summary="通过编码获取字典�?,
    description="通过分组编码获取该分组下的所有字典项",
)
async def get_dict_items_by_group_code(
    group_code: str,
    include_disabled: bool = Query(False, description="是否包含禁用的项")
):
    """通过分组编码获取字典""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        items_data = db.get_dict_data_by_type(group_code, include_disabled)
        # 转换为前端期望的格式
        items = []
        for item in items_data:
            type_data = db.get_dict_type_by_code(item["dict_type"])
            group_id = type_data["dict_id"] if type_data else 0
            items.append({
                "id": item["dict_code"],
                "group_id": group_id,
                "item_code": item["dict_value"],
                "item_name": item["dict_label"],
                "item_value": item.get("data_type", ""),
                "description": item["remark"],
                "status": item["status"],
                "sort_order": item["dict_sort"],
                "color": item.get("color")
            })
        return {"status": "success", "data": items}
    except Exception as e:
        logger.error(f"Failed to get dict items by code: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典项失�? {type(e).__name__}")


@router.post(
    "/dict/items",
    summary="创建字典项",
    description="创建新的字典项",
)
async def create_dict_item(data: DictItemCreate):
    """创建字典�?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        type_data = db.get_dict_type(data.group_id)
        if not type_data:
            raise HTTPException(status_code=404, detail="字典分组不存在")
        dict_type = type_data["dict_type"]
        # 检查是否已存在相同的item_code
        existing = db.get_dict_data_by_value(dict_type, data.item_code)
        if existing:
            raise HTTPException(status_code=400, detail="字典项编码已存在")
        item_id = db.add_dict_data(
            dict_type=dict_type,
            dict_label=data.item_name,
            dict_value=data.item_code,
            dict_sort=data.sort_order,
            data_type=data.item_value or "",
            remark=data.description,
            color=data.color
        )
        return {"status": "success", "data": {"id": item_id}, "message": "创建成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create dict item: {e}")
        raise HTTPException(status_code=500, detail=f"创建字典项失�? {type(e).__name__}")


@router.put(
    "/dict/items/{item_id}",
    summary="更新字典�?,
    description="更新指定字典项的信息",
)
async def update_dict_item(item_id: int, data: DictItemUpdate):
    """更新字典项""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        item_data = db.get_dict_data(item_id)
        if not item_data:
            raise HTTPException(status_code=404, detail="字典项不存在")
        db.update_dict_data(
            dict_code=item_id,
            dict_label=data.item_name,
            dict_value=data.item_value,
            dict_sort=data.sort_order,
            data_type=data.item_value,
            status=data.status,
            remark=data.description,
            color=data.color
        )
        return {"status": "success", "message": "更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update dict item: {e}")
        raise HTTPException(status_code=500, detail=f"更新字典项失�? {type(e).__name__}")


@router.delete(
    "/dict/items/{item_id}",
    summary="删除字典项",
    description="删除指定字典项",
)
async def delete_dict_item(item_id: int):
    """删除字典�?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        item_data = db.get_dict_data(item_id)
        if not item_data:
            raise HTTPException(status_code=404, detail="字典项不存在")
        db.delete_dict_data(item_id)
        return {"status": "success", "message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dict item: {e}")
        raise HTTPException(status_code=500, detail=f"删除字典项失�? {type(e).__name__}")



# ==================== 字典数据初始化API ====================

@router.get(
    "/dict/status",
    summary="获取字典数据状�?,
    description="获取当前字典数据的初始化状态和统计信息",
)
async def get_dict_status():
    """获取字典数据状�?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)

        from gw2_log_score.database.dict_init import DictionaryDataInitializer
        initializer = DictionaryDataInitializer(db)
        summary = initializer.get_current_data_summary()

        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        logger.error(f"Failed to get dict status: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典状态失�? {type(e).__name__}")


@router.post(
    "/dict/initialize",
    summary="初始化字典数�?,
    description="从配置文件初始化字典数据到数据库",
)
async def initialize_dict_data():
    """初始化字典数�?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)

        from gw2_log_score.database.dict_init import DictionaryDataInitializer
        initializer = DictionaryDataInitializer(db)
        results = initializer.initialize_all()

        return {
            "status": "success",
            "message": "字典数据初始化完�?,
            "data": results
        }
    except Exception as e:
        logger.error(f"Failed to initialize dict data: {e}")
        raise HTTPException(status_code=500, detail=f"初始化字典数据失�? {type(e).__name__}")


# ==================== 字典工具API ====================

@router.get(
    "/dict/utils/label/{dict_type}",
    summary="获取字典标签",
    description="根据字典类型和字典值获取字典标�?,
)
async def api_get_dict_label(
    dict_type: str = Path(..., description="字典类型"),
    dict_value: str = Query(..., description="字典�?),
    separator: str = Query(",", description="分隔�?),
):
    """获取字典标签"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        label = get_dict_label(dict_type, dict_value, separator, db)
        return {"status": "success", "data": label}
    except Exception as e:
        logger.error(f"Failed to get dict label: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典标签失败: {type(e).__name__}")


@router.get(
    "/dict/utils/value/{dict_type}",
    summary="获取字典�?,
    description="根据字典类型和字典标签获取字典�?,
)
async def api_get_dict_value(
    dict_type: str = Path(..., description="字典类型"),
    dict_label: str = Query(..., description="字典标签"),
    separator: str = Query(",", description="分隔�?),
):
    """获取字典�?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        value = get_dict_value(dict_type, dict_label, separator, db)
        return {"status": "success", "data": value}
    except Exception as e:
        logger.error(f"Failed to get dict value: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典值失�? {type(e).__name__}")


@router.get(
    "/dict/utils/datas/{dict_type}",
    summary="获取字典数据列表",
    description="根据字典类型获取所有字典数�?,
)
async def api_get_dict_datas(
    dict_type: str = Path(..., description="字典类型"),
):
    """获取字典数据列表"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        datas = get_dict_datas(dict_type, db)
        return {"status": "success", "data": datas}
    except Exception as e:
        logger.error(f"Failed to get dict datas: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典数据失败: {type(e).__name__}")


@router.get(
    "/dict/utils/options/{dict_type}",
    summary="获取字典选项",
    description="根据字典类型获取字典选项（用于下拉选择�?,
)
async def api_get_dict_options(
    dict_type: str = Path(..., description="字典类型"),
):
    """获取字典选项"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        options = get_dict_options(dict_type, db)
        return {"status": "success", "data": options}
    except Exception as e:
        logger.error(f"Failed to get dict options: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典选项失败: {type(e).__name__}")


@router.get(
    "/dict/utils/values/{dict_type}",
    summary="获取字典所有�?,
    description="根据字典类型获取所有字典�?,
)
async def api_get_dict_values(
    dict_type: str = Path(..., description="字典类型"),
):
    """获取字典所有�?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        values = get_dict_values(dict_type, db)
        return {"status": "success", "data": values}
    except Exception as e:
        logger.error(f"Failed to get dict values: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典值失�? {type(e).__name__}")


@router.get(
    "/dict/utils/labels/{dict_type}",
    summary="获取字典所有标�?,
    description="根据字典类型获取所有字典标�?,
)
async def api_get_dict_labels(
    dict_type: str = Path(..., description="字典类型"),
):
    """获取字典所有标�?""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        labels = get_dict_labels(dict_type, db)
        return {"status": "success", "data": labels}
    except Exception as e:
        logger.error(f"Failed to get dict labels: {e}")
        raise HTTPException(status_code=500, detail=f"获取字典标签失败: {type(e).__name__}")


@router.get(
    "/dict/utils/profession/{english_name}",
    summary="获取职业中文名称",
    description="根据职业英文名称获取中文名称",
)
async def api_get_profession_chinese_name(
    english_name: str = Path(..., description="职业英文名称"),
):
    """获取职业中文名称"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        chinese_name = get_profession_chinese_name(english_name, db)
        return {"status": "success", "data": chinese_name}
    except Exception as e:
        logger.error(f"Failed to get profession chinese name: {e}")
        raise HTTPException(status_code=500, detail=f"获取职业中文名称失败: {type(e).__name__}")


@router.get(
    "/dict/utils/specialization/{english_name}",
    summary="获取精英特长中文名称",
    description="根据精英特长英文名称获取中文名称",
)
async def api_get_specialization_chinese_name(
    english_name: str = Path(..., description="精英特长英文名称"),
):
    """获取精英特长中文名称"""
    try:
        ensure_db_exists()
        db = DBManager(db_path)
        chinese_name = get_specialization_chinese_name(english_name, db)
        return {"status": "success", "data": chinese_name}
    except Exception as e:
        logger.error(f"Failed to get specialization chinese name: {e}")
        raise HTTPException(status_code=500, detail=f"获取精英特长中文名称失败: {type(e).__name__}")


@router.post(
    "/dict/utils/cache/clear",
    summary="清空字典缓存",
    description="清空所有字典缓�?,
)
async def api_clear_dict_cache():
    """清空字典缓存"""
    try:
        clear_dict_cache()
        return {"status": "success", "message": "字典缓存已清�?}
    except Exception as e:
        logger.error(f"Failed to clear dict cache: {e}")
        raise HTTPException(status_code=500, detail=f"清空字典缓存失败: {type(e).__name__}")


@router.delete(
    "/dict/utils/cache/{dict_type}",
    summary="删除指定字典缓存",
    description="删除指定字典类型的缓�?,
)
async def api_remove_dict_cache(
    dict_type: str = Path(..., description="字典类型"),
):
    """删除指定字典缓存"""
    try:
        remove_dict_cache(dict_type)
        return {"status": "success", "message": f"字典缓存 [{dict_type}] 已删�?}
    except Exception as e:
        logger.error(f"Failed to remove dict cache: {e}")
        raise HTTPException(status_code=500, detail=f"删除字典缓存失败: {type(e).__name__}")


