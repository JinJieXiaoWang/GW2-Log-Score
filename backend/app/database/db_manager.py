#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块
负责数据库的初始化、迁移和基本操作
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class DBManager:
    """
    数据库管理器
    负责数据库的初始化、迁移和基本操作
    """

    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器
        Args:
            db_path: 数据库文件路径
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "databases",
                "gw2_logs.db",
            )
        self.db_path = db_path
        self._init_db()
        self._migrate_db()
    
    def get_connection(self):
        """
        获取数据库连接
        
        Returns:
            sqlite3.Connection: 数据库连接
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        # 设置连接编码为UTF-8
        conn.text_factory = lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
        # 执行PRAGMA语句确保数据库使用UTF-8编码
        cursor = conn.cursor()
        cursor.execute('PRAGMA encoding="UTF-8"')
        conn.commit()
        cursor.close()
        return conn
    
    def with_connection(self, callback):
        """
        使用数据库连接执行回调函数
        
        Args:
            callback: 回调函数，接收cursor作为参数
        
        Returns:
            回调函数的返回值
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                result = callback(cursor)
                conn.commit()
                return result
            except Exception as e:
                conn.rollback()
                raise

    def _init_db(self):
        """
        初始化数据库，创建必要的表
        
        功能：创建数据库表结构，包括玩家表、战斗日志表、战斗评分表、文件指纹表、字典类型表、字典数据表和评分规则表
        流程：
        1. 确保数据库目录存在
        2. 连接数据库
        3. 创建各个表结构
        4. 提交事务
        """
        # 确保数据库目录存在
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建玩家表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    name TEXT PRIMARY KEY,
                    profession TEXT,
                    role TEXT,
                    account TEXT
                )
            """)

            # 创建战斗日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS combat_logs (
                    log_id TEXT PRIMARY KEY,
                    mode TEXT,
                    encounter_name TEXT,
                    date TEXT,
                    duration INTEGER,
                    log_path TEXT,
                    recorder TEXT
                )
            """)

            # 创建战斗评分表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS combat_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_id TEXT,
                    player_name TEXT,
                    score_dps REAL,
                    score_cc REAL,
                    score_survival REAL,
                    score_boon REAL,
                    total_score REAL,
                    details TEXT,
                    FOREIGN KEY(log_id) REFERENCES combat_logs(log_id),
                    FOREIGN KEY(player_name) REFERENCES players(name)
                )
            """)

            # 创建文件指纹表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    log_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(file_name, upload_date)
                )
            """)

            # 字典类型表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sys_dict_type (
                    dict_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dict_name TEXT NOT NULL DEFAULT '',
                    dict_type TEXT NOT NULL DEFAULT '',
                    status INTEGER DEFAULT 0,
                    sort_order INTEGER DEFAULT 0,
                    remark TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(dict_type)
                )
            """)

            # 字典数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sys_dict_data (
                    dict_code INTEGER PRIMARY KEY AUTOINCREMENT,
                    dict_sort INTEGER DEFAULT 0,
                    dict_label TEXT NOT NULL DEFAULT '',
                    dict_value TEXT NOT NULL DEFAULT '',
                    dict_type TEXT NOT NULL DEFAULT '',
                    data_type TEXT DEFAULT '',
                    css_class TEXT,
                    list_class TEXT,
                    is_default INTEGER DEFAULT 0,
                    status INTEGER DEFAULT 0,
                    create_by TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    update_by TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    remark TEXT,
                    FOREIGN KEY(dict_type) REFERENCES sys_dict_type(dict_type)
                )
            """)

            # 评分规则表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scoring_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    rule_config TEXT NOT NULL,
                    version TEXT DEFAULT '1.0',
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _migrate_db(self):
        """
        数据库迁移，处理表结构变更
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 检查并添加缺失的列
            cursor.execute("PRAGMA table_info(combat_logs)")
            columns = [column[1] for column in cursor.fetchall()]

            if "recorder" not in columns:
                cursor.execute("ALTER TABLE combat_logs ADD COLUMN recorder TEXT")

            conn.commit()

    def save_combat_log(self, log_id: str, mode: str, encounter_name: str, date: str, duration: int, log_path: str, recorder: str) -> str:
        """
        保存战斗日志数据

        Args:
            log_id: 日志ID
            mode: 游戏模式
            encounter_name: 遭遇战名称
            date: 日期
            duration: 持续时间
            log_path: 日志路径
            recorder: 记录者
        Returns:
            日志ID
        """
        def callback(cursor):
            # 保存战斗日志
            cursor.execute(
                """
                INSERT OR REPLACE INTO combat_logs 
                (log_id, mode, encounter_name, date, duration, log_path, recorder)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    mode,
                    encounter_name,
                    date,
                    duration,
                    log_path,
                    recorder,
                ),
            )
        
        self.with_connection(callback)
        return log_id

    def save_file_fingerprint(
        self, file_name: str, file_hash: str, log_id: str = None
    ) -> bool:
        """
        保存文件指纹

        Args:
            file_name: 文件名
            file_hash: 文件哈希
            log_id: 日志ID

        Returns:
            是否保存成功
        """
        upload_date = datetime.now().strftime("%Y-%m-%d")

        def callback(cursor):
            try:
                cursor.execute(
                    "INSERT INTO file_fingerprints (file_name, file_hash, " +
                    "upload_date, log_id) VALUES (?, ?, ?, ?)",
                    (file_name, file_hash, upload_date, log_id),
                )
                return True
            except sqlite3.IntegrityError:
                # 文件已存在
                return False
        
        try:
            return self.with_connection(callback)
        except sqlite3.IntegrityError:
            # 文件已存在
            return False

    def get_file_fingerprint(
        self, file_name: str, upload_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取文件指纹

        Args:
            file_name: 文件名
            upload_date: 上传日期

        Returns:
            文件指纹信息
        """
        if upload_date is None:
            upload_date = datetime.now().strftime("%Y-%m-%d")

        def callback(cursor):
            cursor.execute(
                "SELECT * FROM file_fingerprints WHERE file_name = ? AND upload_date = ?",
                (file_name, upload_date),
            )
            result = cursor.fetchone()

            if result:
                return {
                    "id": result[0],
                    "file_name": result[1],
                    "file_hash": result[2],
                    "upload_date": result[3],
                    "log_id": result[4],
                    "created_at": result[5],
                }
            return None
        
        return self.with_connection(callback)

    def get_combat_logs(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取战斗日志列表

        Args:
            limit: 限制数量
            offset: 偏移量
        Returns:
            战斗日志列表
        """
        def callback(cursor):
            cursor.execute(
                "SELECT * FROM combat_logs ORDER BY date DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            results = cursor.fetchall()

            logs = []
            for result in results:
                logs.append(
                    {
                        "log_id": result[0],
                        "mode": result[1],
                        "encounter_name": result[2],
                        "date": result[3],
                        "duration": result[4],
                        "log_path": result[5],
                        "recorder": result[6],
                    }
                )

            return logs
        
        return self.with_connection(callback)

    def get_combat_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个战斗日志

        Args:
            log_id: 日志ID

        Returns:
            战斗日志信息
        """
        def callback(cursor):
            cursor.execute(
                "SELECT * FROM combat_logs WHERE log_id = ?",
                (log_id,),
            )
            result = cursor.fetchone()

            if result:
                return {
                    "log_id": result[0],
                    "mode": result[1],
                    "encounter_name": result[2],
                    "date": result[3],
                    "duration": result[4],
                    "log_path": result[5],
                    "recorder": result[6],
                }
            return None
        
        return self.with_connection(callback)

    def get_combat_scores(self, log_id: str) -> List[Dict[str, Any]]:
        """
        获取战斗评分

        Args:
            log_id: 日志ID

        Returns:
            战斗评分列表
        """
        def callback(cursor):
            cursor.execute(
                "SELECT * FROM combat_scores WHERE log_id = ?",
                (log_id,),
            )
            results = cursor.fetchall()

            scores = []
            for result in results:
                scores.append(
                    {
                        "id": result[0],
                        "log_id": result[1],
                        "player_name": result[2],
                        "score_dps": result[3],
                        "score_cc": result[4],
                        "score_survival": result[5],
                        "score_boon": result[6],
                        "total_score": result[7],
                        "details": json.loads(result[8]) if result[8] else {},
                    }
                )

            return scores
        
        return self.with_connection(callback)

    def clear_today_data(self) -> int:
        """
        清除当天的数据
        Returns:
            删除的记录数
        """
        today = datetime.now().strftime("%Y-%m-%d")
        deleted_count = 0

        def callback(cursor):
            nonlocal deleted_count
            # 获取当天的日志ID
            cursor.execute(
                "SELECT log_id FROM combat_logs WHERE date LIKE ?",
                (f"{today}%",),
            )
            log_ids = [result[0] for result in cursor.fetchall()]

            if log_ids:
                # 删除评分数据
                cursor.execute(
                    "DELETE FROM combat_scores WHERE log_id IN (" 
                    + ",".join(["?"] * len(log_ids)) 
                    + ")",
                    log_ids,
                )
                deleted_count += cursor.rowcount

                # 删除日志数据
                cursor.execute(
                    "DELETE FROM combat_logs WHERE log_id IN (" 
                    + ",".join(["?"] * len(log_ids)) 
                    + ")",
                    log_ids,
                )
                deleted_count += cursor.rowcount

            # 删除文件指纹
            cursor.execute(
                "DELETE FROM file_fingerprints WHERE upload_date = ?",
                (today,),
            )
            deleted_count += cursor.rowcount

        self.with_connection(callback)
        return deleted_count

    def clear_all_data(self) -> int:
        """
        清除所有数据
        Returns:
            删除的记录数
        """
        deleted_count = 0

        def callback(cursor):
            nonlocal deleted_count
            # 删除评分数据
            cursor.execute("DELETE FROM combat_scores")
            deleted_count += cursor.rowcount

            # 删除日志数据
            cursor.execute("DELETE FROM combat_logs")
            deleted_count += cursor.rowcount

            # 删除文件指纹
            cursor.execute("DELETE FROM file_fingerprints")
            deleted_count += cursor.rowcount

        self.with_connection(callback)
        return deleted_count

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息
        """
        def callback(cursor):
            # 总日志数
            cursor.execute("SELECT COUNT(*) FROM combat_logs")
            total_logs = cursor.fetchone()[0]

            # 总玩家数
            cursor.execute("SELECT COUNT(*) FROM players")
            total_players = cursor.fetchone()[0]

            # 今日日志数
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COUNT(*) FROM combat_logs WHERE date LIKE ?",
                (f"{today}%",),
            )
            today_logs = cursor.fetchone()[0]

            return {
                "total_logs": total_logs,
                "total_players": total_players,
                "today_logs": today_logs,
            }
        
        return self.with_connection(callback)

    def get_all_logs(self) -> List[Dict[str, Any]]:
        """
        获取所有战斗日志记录
        Returns:
            包含所有日志记录的列表，按日期降序排列
        """
        def callback(cursor):
            cursor.execute(
                "SELECT * FROM combat_logs ORDER BY date DESC"
            )
            results = cursor.fetchall()

            logs = []
            for result in results:
                logs.append(
                    {
                        "log_id": result[0],
                        "mode": result[1],
                        "encounter_name": result[2],
                        "date": result[3],
                        "duration": result[4],
                        "log_path": result[5],
                        "recorder": result[6],
                    }
                )

            return logs
        
        return self.with_connection(callback)

    def get_log_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        根据文件哈希获取日志

        Args:
            file_hash: 文件哈希值
        Returns:
            日志信息
        """
        def callback(cursor):
            cursor.execute(
                "SELECT cl.* FROM combat_logs cl JOIN file_fingerprints ff ON cl.log_id = ff.log_id WHERE ff.file_hash = ?",
                (file_hash,),
            )
            result = cursor.fetchone()

            if result:
                return {
                    "log_id": result[0],
                    "mode": result[1],
                    "encounter_name": result[2],
                    "date": result[3],
                    "duration": result[4],
                    "log_path": result[5],
                    "recorder": result[6],
                }
            return None
        
        return self.with_connection(callback)

    def save_player(self, name: str, profession: str, role: str, account: str) -> bool:
        """
        保存玩家信息

        Args:
            name: 玩家名称
            profession: 职业
            role: 角色定位
            account: 账户名
        Returns:
            是否保存成功
        """
        def callback(cursor):
            cursor.execute(
                """
                INSERT OR REPLACE INTO players (name, profession, role, account)
                VALUES (?, ?, ?, ?)
                """,
                (name, profession, role, account),
            )
            return True
        
        try:
            self.with_connection(callback)
            return True
        except sqlite3.Error as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"保存玩家信息失败: {e}")
            return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"保存玩家信息时发生未知错误: {e}")
            return False

    def save_score(self, log_id: str, player_name: str, score_dps: float, score_cc: float, score_survival: float, score_boon: float, total_score: float, details: str) -> bool:
        """
        保存评分数据

        Args:
            log_id: 日志ID
            player_name: 玩家名称
            score_dps: DPS评分
            score_cc: CC评分
            score_survival: 生存评分
            score_boon: 增益评分
            total_score: 总分
            details: 详细信息

        Returns:
            是否保存成功
        """
        def callback(cursor):
            cursor.execute(
                """
                INSERT OR REPLACE INTO combat_scores 
                (log_id, player_name, score_dps, score_cc, score_survival, score_boon, total_score, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (log_id, player_name, score_dps, score_cc, score_survival, score_boon, total_score, details),
            )
            return True
        
        try:
            self.with_connection(callback)
            return True
        except sqlite3.Error as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"保存评分数据失败: {e}")
            return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"保存评分数据时发生未知错误: {e}")
            return False

    def get_scores_by_log(self, log_id: str) -> List[Dict[str, Any]]:
        """
        获取指定日志的评分
        Args:
            log_id: 日志ID

        Returns:
            评分数据列表
        """
        def callback(cursor):
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

            scores = []
            for row in cursor.fetchall():
                score = dict(row)
                if score.get("details"):
                    try:
                        score["details"] = json.loads(score["details"])
                    except (json.JSONDecodeError, TypeError):
                        pass
                scores.append(score)

            return scores
        
        return self.with_connection(callback)

    def get_dict_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有字典分类
        Returns:
            字典分类列表
        """
        def callback(cursor):
            cursor.execute("SELECT * FROM sys_dict_type WHERE status = 0 ORDER BY sort_order")
            categories = [dict(row) for row in cursor.fetchall()]
            return categories
        
        return self.with_connection(callback)

    def get_dict_by_category(self, category_code: str) -> List[Dict[str, Any]]:
        """
        获取分组下的字典

        Args:
            category_code: 分类编码

        Returns:
            字典列表
        """
        def callback(cursor):
            cursor.execute(
                "SELECT * FROM sys_dict_data WHERE dict_type = ? AND status = 0 ORDER BY dict_sort",
                (category_code,),
            )
            datas = [dict(row) for row in cursor.fetchall()]
            return datas
        
        return self.with_connection(callback)

    def get_dict_by_id(self, dict_id: int) -> Dict[str, Any]:
        """
        通过ID获取字典详情

        Args:
            dict_id: 字典ID

        Returns:
            字典详情
        """
        def callback(cursor):
            cursor.execute("SELECT * FROM sys_dict_data WHERE dict_code = ?", (dict_id,))
            result = cursor.fetchone()
            if result:
                return dict(result)
            return {}
        
        return self.with_connection(callback)

    def get_dict_by_code(self, category_code: str, dict_value: str) -> Dict[str, Any]:
        """
        通过分组编码和字典值获取字典
        Args:
            category_code: 分类编码
            dict_value: 字典值
        Returns:
            字典详情
        """
        def callback(cursor):
            cursor.execute(
                "SELECT * FROM sys_dict_data WHERE dict_type = ? AND dict_value = ? AND status = 0",
                (category_code, dict_value),
            )
            result = cursor.fetchone()
            if result:
                return dict(result)
            return {}
        
        return self.with_connection(callback)

    def create_dict_group(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建字典分组
        Args:
            data: 分组数据，包含dict_code, dict_name, remark, status, sort_order
        Returns:
            创建的分组信息
        """
        def callback(cursor):
            cursor.execute(
                """
                INSERT INTO sys_dict_type (dict_name, dict_type, status, sort_order, remark)
                VALUES (?, ?, ?, ?, ?)
                """,
                (data.get('dict_name'), data.get('dict_type'), data.get('status', 0), data.get('sort_order', 0), data.get('remark', ''))
            )
            dict_id = cursor.lastrowid
            cursor.execute("SELECT * FROM sys_dict_type WHERE dict_id = ?", (dict_id,))
            result = cursor.fetchone()
            return dict(result) if result else {}
        
        return self.with_connection(callback)

    def update_dict_group(self, dict_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新字典分组
        Args:
            dict_id: 分组ID
            data: 分组数据，包含dict_name, remark, status, sort_order
        Returns:
            更新后的分组信息
        """
        def callback(cursor):
            cursor.execute(
                """
                UPDATE sys_dict_type
                SET dict_name = ?, status = ?, sort_order = ?, remark = ?, updated_at = CURRENT_TIMESTAMP
                WHERE dict_id = ?
                """,
                (data.get('dict_name'), data.get('status', 0), data.get('sort_order', 0), data.get('remark', ''), dict_id)
            )
            cursor.execute("SELECT * FROM sys_dict_type WHERE dict_id = ?", (dict_id,))
            result = cursor.fetchone()
            return dict(result) if result else {}
        
        return self.with_connection(callback)

    def delete_dict_group(self, dict_id: int) -> bool:
        """
        删除字典分组
        Args:
            dict_id: 分组ID
        Returns:
            是否删除成功
        """
        def callback(cursor):
            # 先删除该分组下的所有字典项
            cursor.execute("SELECT dict_type FROM sys_dict_type WHERE dict_id = ?", (dict_id,))
            result = cursor.fetchone()
            if result:
                dict_type = result[0]
                cursor.execute("DELETE FROM sys_dict_data WHERE dict_type = ?", (dict_type,))
            # 删除分组
            cursor.execute("DELETE FROM sys_dict_type WHERE dict_id = ?", (dict_id,))
            return cursor.rowcount > 0
        
        return self.with_connection(callback)

    def get_dict_items_by_group(self, dict_type: str, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """
        获取分组下的字典项
        Args:
            dict_type: 分组类型
            include_disabled: 是否包含禁用项
        Returns:
            字典项列表
        """
        def callback(cursor):
            if include_disabled:
                cursor.execute(
                    "SELECT * FROM sys_dict_data WHERE dict_type = ? ORDER BY dict_sort",
                    (dict_type,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM sys_dict_data WHERE dict_type = ? AND status = 0 ORDER BY dict_sort",
                    (dict_type,)
                )
            items = [dict(row) for row in cursor.fetchall()]
            return items
        
        return self.with_connection(callback)

    def create_dict_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建字典项
        Args:
            data: 字典项数据，包含group_id, item_code, item_name, item_value, description, status, sort_order, color
        Returns:
            创建的字典项信息
        """
        def callback(cursor):
            # 获取分组类型
            cursor.execute("SELECT dict_type FROM sys_dict_type WHERE dict_id = ?", (data.get('group_id'),))
            result = cursor.fetchone()
            if not result:
                return {}
            dict_type = result[0]
            
            cursor.execute(
                """
                INSERT INTO sys_dict_data (dict_sort, dict_label, dict_value, dict_type, css_class, status, remark)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get('sort_order', 0),
                    data.get('item_name'),
                    data.get('item_code'),
                    dict_type,
                    data.get('color', ''),
                    data.get('status', 1),
                    data.get('description', '')
                )
            )
            dict_code = cursor.lastrowid
            cursor.execute("SELECT * FROM sys_dict_data WHERE dict_code = ?", (dict_code,))
            result = cursor.fetchone()
            return dict(result) if result else {}
        
        return self.with_connection(callback)

    def update_dict_item(self, dict_code: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新字典项
        Args:
            dict_code: 字典项ID
            data: 字典项数据，包含item_name, item_value, description, status, sort_order, color
        Returns:
            更新后的字典项信息
        """
        def callback(cursor):
            cursor.execute(
                """
                UPDATE sys_dict_data
                SET dict_sort = ?, dict_label = ?, dict_value = ?, css_class = ?, status = ?, remark = ?, updated_at = CURRENT_TIMESTAMP
                WHERE dict_code = ?
                """,
                (
                    data.get('sort_order', 0),
                    data.get('item_name'),
                    data.get('item_code'),
                    data.get('color', ''),
                    data.get('status', 1),
                    data.get('description', ''),
                    dict_code
                )
            )
            cursor.execute("SELECT * FROM sys_dict_data WHERE dict_code = ?", (dict_code,))
            result = cursor.fetchone()
            return dict(result) if result else {}
        
        return self.with_connection(callback)

    def delete_dict_item(self, dict_code: int) -> bool:
        """
        删除字典项
        Args:
            dict_code: 字典项ID
        Returns:
            是否删除成功
        """
        def callback(cursor):
            cursor.execute("DELETE FROM sys_dict_data WHERE dict_code = ?", (dict_code,))
            return cursor.rowcount > 0
        
        return self.with_connection(callback)


# 创建数据库管理器实例
db_manager = DBManager()
