#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评分服务

封装评分相关的核心业务逻辑
"""

import json
from typing import Dict, Any, List, Optional
from app.database.db_manager import DBManager
from app.core.logger import Logger


class ScoreService:
    """评分服务类"""

    def __init__(self, db_path: str):
        """
        初始化评分服务

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.logger = Logger(__name__)

    def get_scores(self, log_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取战斗评分数据

        支持两种模式:
        - 不指定log_id: 返回所有评分记录
        - 指定log_id: 返回该特定日志的所有评分

        Args:
            log_id: 可选的日志ID，指定则返回该日志的评分

        Returns:
            评分数据列表
        """
        import sqlite3

        with sqlite3.connect(self.db_path) as conn:
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

        return scores

    def get_log_scores(self, log_id: str) -> List[Dict[str, Any]]:
        """
        获取指定日志的评分详情

        Args:
            log_id: 日志唯一标识符

        Returns:
            该日志的所有玩家评分，按总分降序排列
        """
        db = DBManager(self.db_path)
        return db.get_scores_by_log(log_id)

    def get_today_scores(self) -> List[Dict[str, Any]]:
        """
        获取今日评分数据

        Returns:
            今日评分数据列表
        """
        import sqlite3
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT cs.*, cl.date, cl.encounter_name, cl.mode,
                       p.profession, p.role, p.account
                FROM combat_scores cs
                LEFT JOIN combat_logs cl ON cs.log_id = cl.log_id
                LEFT JOIN players p ON cs.player_name = p.name
                WHERE cl.date LIKE ?
                ORDER BY cs.total_score DESC
            """,
                (f"{today}%",),
            )

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

        return scores
