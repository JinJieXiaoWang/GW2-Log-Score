#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GW2战斗日志解析器主模块

提供统一的日志解析接口，支持JSON和ZEVTC格式日志文件
"""

import os
from typing import Dict, Any
from app.core.logger import Logger
from app.parser.base_parser import BaseParser
from app.parser.json_handler import JSONHandler
from app.parser.evtc_handler import EVTCHandler
from app.parser.mode_detector import ModeDetector
from app.parser.player_parser import PlayerParser

logger = Logger(__name__)


class GW2LogParser(BaseParser):
    """
    GW2战斗日志解析器
    支持解析的格式
    - JSON格式 (EI导出的data.json)
    - ZEVTC格式 (arcdps原生日志格式)
    - EVTC格式 (arcdps原生日志格式)

    使用示例:
        parser = GW2LogParser()
        data = parser.parse_file('path/to/log.json')  # 解析JSON文件
        data = parser.parse_file('path/to/log.zevtc')  # 解析ZEVTC文件
        print(data['encounter_name'])
    """

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析日志文件

        Args:
            file_path: 日志文件路径

        Returns:
            解析后的战斗数据字典
        """
        return self.parse_file(file_path)

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析日志文件，支持JSON和ZEVTC格式

        Args:
            file_path: 日志文件路径

        Returns:
            解析后的战斗数据字典，包含
            - log_id: 日志唯一标识
            - encounter_name: 战斗名称
            - duration: 战斗时长(秒)
            - duration_ms: 战斗时长(毫秒)
            - recorded_by: 记录者
            - date: 战斗日期
            - mode: 游戏模式
            - players: 玩家数据列表

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        self.validate_file(file_path)

        ext = self.get_file_extension(file_path)

        if ext in [".json"]:
            logger.info(f"Parsing JSON log file: {file_path}")
            return self._parse_json_file(file_path)
        elif ext in [".zevtc", ".evtc", ".zetvc"]:
            logger.info(f"Parsing ZEVTC log file: {file_path}")
            return EVTCHandler.process(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {ext}. Only JSON and ZEVTC files are supported."
            )

    def _parse_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析JSON格式日志文件

        Args:
            file_path: JSON文件路径

        Returns:
            解析后的战斗数据字典
        """
        raw_data = JSONHandler.read(file_path)
        return self._process_json_data(raw_data, file_path)

    def _process_json_data(
        self, data: Dict[str, Any], file_path: str
    ) -> Dict[str, Any]:
        """
        处理JSON数据，标准化为统一格式

        Args:
            data: 原始JSON数据
            file_path: 原始文件路径

        Returns:
            标准化后的战斗数据字典
        """
        encounter_name = self._extract_encounter_name(data)
        duration_ms = self._extract_duration_ms(data)
        duration_s = duration_ms / 1000
        recorded_by = data.get("recordedBy", "Unknown")
        time_start = data.get("timeStart", "")
        mode = ModeDetector.detect(data)
        log_id = os.path.basename(file_path)

        players = PlayerParser.parse_all(data.get("players", []), duration_s)

        fight_name = encounter_name  # 对于JSON，使用encounter_name

        result = {
            "log_id": log_id,
            "encounter_name": encounter_name,
            "fightName": fight_name,
            "duration": duration_s,
            "duration_ms": duration_ms,
            "durationMS": duration_ms,
            "recorded_by": recorded_by,
            "date": time_start,
            "timeStart": time_start,
            "mode": mode,
            "players": players,
            "phases": data.get(
                "phases", [{"name": "Full Fight", "start": 0, "end": duration_ms}]
            ),
            "targets": data.get("targets", []),
            "success": data.get("success", True),
            "isCM": data.get("isCM", False),
            "detailedWvW": data.get("detailedWvW", False),
            "language": data.get("language", "Chinese"),
            "languageID": data.get("languageID", 5),
            "gW2Build": data.get("gW2Build", 0),
        }

        logger.info(
            f"Parsed log: {encounter_name}, "
            f"duration: {duration_s:.1f}s, "
            f"mode: {mode}, "
            f"players: {len(players)}"
        )

        return result

    @staticmethod
    def _extract_encounter_name(data: Dict[str, Any]) -> str:
        """
        提取战斗名称

        Args:
            data: 原始数据

        Returns:
            战斗名称
        """
        return data.get("fightName") or data.get("encounterName") or "Unknown"

    @staticmethod
    def _extract_duration_ms(data: Dict[str, Any]) -> float:
        """
        提取战斗时长(毫秒)

        Args:
            data: 原始数据

        Returns:
            战斗时长(毫秒)
        """
        duration_ms = data.get("durationMS", 0)
        try:
            return float(duration_ms)
        except (ValueError, TypeError):
            return 0.0
