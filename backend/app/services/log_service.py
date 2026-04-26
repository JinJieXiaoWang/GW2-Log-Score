#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志服务

封装日志上传、解析和保存的核心业务逻辑
"""

import os
import tempfile
import shutil
import json
import uuid
from typing import Dict, Any, List
from app.parser.gw2_log_parser import GW2LogParser
from app.scoring.scoring_engine import ScoringEngine
from app.database.db_manager import DBManager
from app.core.logger import Logger


class LogService:
    """日志服务类"""

    def __init__(self, db_path: str):
        """
        初始化日志服务

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.logger = Logger(__name__)
        self.ensure_db_exists()

    def ensure_db_exists(self) -> None:
        """
        确保数据库文件存在，如不存在则初始化
        """
        if not os.path.exists(self.db_path):
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            DBManager(self.db_path)

    def compute_file_hash(self, file_path: str) -> str:
        """
        计算文件的MD5哈希值，用于检测重复上传

        Args:
            file_path: 文件路径

        Returns:
            MD5哈希字符串

        Raises:
            FileNotFoundError: 文件不存在
            PermissionError: 没有文件读取权限
            IOError: 文件读取失败
        """
        import hashlib

        try:
            hash_obj = hashlib.md5()
            with open(file_path, "rb") as f:
                hash_obj.update(f.read())
            return hash_obj.hexdigest()
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except PermissionError:
            self.logger.error(f"Permission denied: {file_path}")
            raise
        except IOError as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise

    def save_parsed_data(
        self, parsed_data: Dict[str, Any], file_hash: str, log_id: str, filename: str
    ) -> List[Dict[str, Any]]:
        """
        保存解析后的数据到数据库

        Args:
            parsed_data: 解析后的日志数据
            file_hash: 文件哈希值
            log_id: 日志唯一标识
            filename: 文件名

        Returns:
            评分结果列表

        Raises:
            KeyError: 解析数据缺少必要字段
            DatabaseError: 数据库操作失败
            JSONEncodeError: JSON编码失败
        """
        try:
            db = DBManager(self.db_path)

            # 验证必要字段
            required_fields = ["mode", "encounter_name", "duration", "players"]
            for field in required_fields:
                if field not in parsed_data:
                    raise KeyError(f"Missing required field: {field}")

            # 保存战斗日志
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

            # 保存玩家信息
            for p in parsed_data["players"]:
                if "name" not in p or "profession" not in p:
                    self.logger.warning(f"Skipping player without name or profession: {p}")
                    continue
                db.save_player(
                    p["name"], p["profession"], p.get("role", ""), p.get("account", "")
                )

            # 计算评分
            try:
                engine = ScoringEngine()
                scores = engine.calculate_scores(parsed_data)
            except Exception as e:
                self.logger.error(f"Error calculating scores: {e}")
                raise ValueError(f"Score calculation failed: {e}")

            # 保存评分数据
            for s in scores:
                try:
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
                        # 旧格式兼容
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
                except Exception as e:
                    self.logger.error(f"Error saving score for player {s.get('player_name', 'unknown')}: {e}")
                    continue

            return scores
        except KeyError as e:
            self.logger.error(f"Missing required data field: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON encoding error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error saving parsed data: {e}")
            raise

    def _validate_file_extension(self, filename: str) -> str:
        """
        验证文件扩展名

        Args:
            filename: 文件名

        Returns:
            文件扩展名

        Raises:
            ValueError: 文件格式不支持
        """
        allowed_extensions = ['.json', '.evtc', '.zevtc', '.zetvc']
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise ValueError(f"Unsupported file format: {file_ext}. Allowed formats: {', '.join(allowed_extensions)}")
        return file_ext

    def _save_temp_file(self, file, temp_dir: str, filename: str) -> str:
        """
        保存临时文件

        Args:
            file: 上传的文件对象
            temp_dir: 临时目录路径
            filename: 文件名

        Returns:
            临时文件路径

        Raises:
            ValueError: 文件保存失败
        """
        file_path = os.path.join(temp_dir, filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return file_path
        except IOError as e:
            self.logger.error(f"Error saving temporary file: {e}")
            raise ValueError(f"Failed to save file: {e}")

    def _validate_file(self, file_path: str, file_ext: str) -> None:
        """
        验证文件大小和内容类型

        Args:
            file_path: 文件路径
            file_ext: 文件扩展名

        Raises:
            ValueError: 文件验证失败
        """
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("Empty file")
        
        # 检查文件大小限制
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise ValueError(f"File too large. Maximum size: {max_size / (1024 * 1024)}MB")
        
        # 检查文件内容类型
        try:
            import magic
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(file_path)
            self.logger.info(f"File MIME type: {mime_type}")
            
            # 验证文件类型
            if file_ext == '.json' and 'json' not in mime_type:
                raise ValueError("Invalid JSON file")
            elif file_ext == '.evtc' and mime_type != 'application/octet-stream':
                self.logger.warning(f"Unexpected MIME type for EVTC file: {mime_type}")
            elif file_ext in ['.zevtc', '.zetvc'] and 'zip' not in mime_type:
                raise ValueError("Invalid compressed file")
        except ImportError:
            self.logger.warning("python-magic not installed, skipping MIME type check")
        except Exception as e:
            self.logger.warning(f"Error checking MIME type: {e}")

    def _check_existing_log(self, file_hash: str) -> tuple:
        """
        检查是否已存在相同内容的日志

        Args:
            file_hash: 文件哈希值

        Returns:
            (is_update, log_id) 元组

        Raises:
            ValueError: 数据库操作失败
        """
        try:
            db = DBManager(self.db_path)
            existing_log = db.get_log_by_hash(file_hash)
            is_update = False

            if existing_log:
                self.logger.info("File with same content already exists")
                is_update = True
                log_id = existing_log["log_id"]
            else:
                log_id = str(uuid.uuid4())
            return is_update, log_id
        except Exception as e:
            self.logger.error(f"Error checking existing log: {e}")
            raise ValueError(f"Database error: {e}")

    def _parse_log_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析日志文件

        Args:
            file_path: 文件路径

        Returns:
            解析后的数据

        Raises:
            ValueError: 解析失败
        """
        try:
            parser = GW2LogParser()
            parsed_data = parser.parse_file(file_path)

            if not parsed_data:
                raise ValueError("Failed to parse log file")
            return parsed_data
        except Exception as e:
            self.logger.error(f"Error parsing log file: {e}")
            raise ValueError(f"Parsing failed: {e}")

    def upload_and_process_log(self, file) -> Dict[str, Any]:
        """
        上传并处理GW2战斗日志文件

        Args:
            file: 上传的文件对象

        Returns:
            处理结果

        Raises:
            ValueError: 文件格式不支持或解析失败
            IOError: 文件保存失败
            DatabaseError: 数据库操作失败
        """
        temp_dir = tempfile.mkdtemp()
        try:
            # 验证文件扩展名
            file_ext = self._validate_file_extension(file.filename)

            # 保存临时文件
            file_path = self._save_temp_file(file, temp_dir, file.filename)

            # 验证文件
            self._validate_file(file_path, file_ext)

            # 计算文件哈希
            try:
                file_hash = self.compute_file_hash(file_path)
            except Exception as e:
                self.logger.error(f"Error computing file hash: {e}")
                raise ValueError(f"Failed to process file: {e}")

            # 检查是否已存在
            is_update, log_id = self._check_existing_log(file_hash)

            # 解析日志文件
            parsed_data = self._parse_log_file(file_path)

            # 保存数据
            try:
                scores = self.save_parsed_data(
                    parsed_data, file_hash, log_id, file.filename
                )
            except Exception as e:
                self.logger.error(f"Error saving parsed data: {e}")
                raise ValueError(f"Data processing failed: {e}")

            self.logger.info("Processing successful")

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
        finally:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    self.logger.warning(f"Error cleaning up temporary directory: {e}")

    def get_all_logs(self) -> List[Dict[str, Any]]:
        """
        获取所有战斗日志记录

        Returns:
            包含所有日志记录的列表，按日期降序排列

        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            self.ensure_db_exists()
            db = DBManager(self.db_path)
            return db.get_all_logs()
        except Exception as e:
            self.logger.error(f"Error getting all logs: {e}")
            raise

    def get_logs_by_mode(self, mode: str = None) -> List[Dict[str, Any]]:
        """
        获取战斗日志历史，支持按游戏模式过滤

        Args:
            mode: 游戏模式过滤(PVE/WvW/PvP等)

        Returns:
            历史战斗记录列表

        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            self.ensure_db_exists()
            import sqlite3

            with sqlite3.connect(self.db_path) as conn:
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

            return logs
        except sqlite3.Error as e:
            self.logger.error(f"SQLite error: {e}")
            raise ValueError(f"Database error: {e}")
        except Exception as e:
            self.logger.error(f"Error getting logs by mode: {e}")
            raise
