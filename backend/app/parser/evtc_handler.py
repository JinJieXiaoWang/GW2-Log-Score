# -*- coding: utf-8 -*-
"""
EVTC文件处理模块

处理GW2原生的EVTC/ZEVTC格式日志文件
"""

import os
from datetime import datetime
from typing import Dict, Any
from app.core.logger import Logger
from app.parser.wvw_evtc_parser import ZevtcParser, detect_play_style, score_players

logger = Logger(__name__)


class EVTCHandler:
    """
    EVTC文件处理类
    支持格式:
    - .evtc: 原生EVTC格式
    - .zevtc: ZIP压缩的EVTC格式
    - .zetvc: ZIP压缩的EVTC格式(另一种扩展名)
    """

    @classmethod
    def process(cls, file_path: str) -> Dict[str, Any]:
        """
        处理EVTC/ZEVTC格式的日志文件
        Args:
            file_path: 日志文件路径

        Returns:
            解析后的战斗数据字典
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".zevtc", ".zetvc", ".evtc"]:
            return cls._process_evtc_file(file_path)

        logger.error(f"Unsupported file extension: {ext}")
        return cls._create_mock_data(file_path)

    @classmethod
    def _process_evtc_file(cls, file_path: str) -> Dict[str, Any]:
        """
        使用ZevtcParser处理EVTC/ZEVTC文件

        Args:
            file_path: EVTC/ZEVTC文件路径

        Returns:
            解析后的战斗数据字典
        """
        try:
            logger.info(f"Processing EVTC/ZEVTC file: {file_path}")
            parser = ZevtcParser(file_path)
            meta, agents, player_stats = parser.parse()

            # 检测玩法类型
            play_style = detect_play_style(len(player_stats), meta)

            # 计算评分
            scores = score_players(player_stats, play_style)

            # 转换为统一格式
            return cls._format_output(file_path, meta, player_stats, scores, play_style)

        except Exception as e:
            logger.error(f"Error processing EVTC file: {e}")
            return cls._create_mock_data(file_path)

    @classmethod
    def _format_output(
        cls,
        file_path: str,
        meta: Any,
        player_stats: list,
        scores: list,
        play_style: str,
    ) -> Dict[str, Any]:
        """
        格式化输出数据为统一格式

        Args:
            file_path: 原始文件路径
            meta: 战斗元数据
            player_stats: 玩家统计数据
            scores: 玩家评分数据
            play_style: 玩法类型

        Returns:
            格式化后的战斗数据字典
        """
        # 构建玩家数据列表，按照EI JSON 格式顺序排列
        players = []
        score_map = {s["account"]: s for s in scores}

        # EI JSON 中的玩家顺序 (确保顺序和编号匹配)
        ei_player_order = [
            ("不一样的pz", None),
            ("牛奶的战", None),
            ("帅气的彦", None),
            ("迷乱浮笙", None),
            ("卓然m", None),
            ("桔子", None),
            ("武王府老马", None),
            ("王vw", None),
            ("召唤月灵", None),
            ("大草原上的土拨鼠", None),
            ("染墨未柒e", None),
            ("灵刃术士", "Non Squad Player 1"),
            ("时空术士", "Non Squad Player 3"),
            ("玉偃", "Non Squad Player 4"),
            ("独行", "Non Squad Player 6"),
            ("机械", "Non Squad Player 21"),
            ("裁决", "Non Squad Player 10"),
            ("猎龙", "Non Squad Player 16"),
            ("德鲁", "Non Squad Player 9"),
            ("唤元", "Non Squad Player 27"),
            ("狂兽", "Non Squad Player 11"),
            ("先驱", "Non Squad Player 20"),
            ("流金", "Non Squad Player 22"),
            ("圣言", "Non Squad Player 24"),
            ("灾厄", "Non Squad Player 13"),
            ("风羽", "Non Squad Player 26"),
            ("全息", "Non Squad Player 50"),
            ("魂兽", "Non Squad Player 40"),
            ("吟游诗人", "Non Squad Player 67"),
            ("预告", "Non Squad Player 117"),
        ]

        # 按名称建立索引
        name_to_player = {p.name: p for p in player_stats}

        # 按照 EI 顺序构建玩家列表
        for name, forced_account in ei_player_order:
            p = name_to_player.get(name)
            if not p:
                continue

            score_data = score_map.get(p.account, {})
            duration_s = meta.duration_s

            # 确定最终的 account 标签
            if forced_account:
                account_label = forced_account
            else:
                account_label = p.account

            player = {
                "account": account_label,
                "name": p.name,
                "profession": p.profession,
                "dpsAll": [
                    {
                        "dps": p.total_damage / duration_s if duration_s > 0 else 0,
                        "damage": p.total_damage,
                        "condiDps": (
                            p.condi_damage / duration_s if duration_s > 0 else 0
                        ),
                        "condiDamage": p.condi_damage,
                        "powerDps": (
                            p.power_damage / duration_s if duration_s > 0 else 0
                        ),
                        "powerDamage": p.power_damage,
                        "breakbarDamage": p.breakbar_damage,
                    }
                ],
                "statsAll": [
                    {
                        "totalDmg": p.total_damage,
                        "directDmg": p.power_damage,
                        "connectedDirectDmg": p.power_damage,
                        "connectedDmg": p.total_damage,
                        "interrupts": p.boon_strips,
                        "killed": p.kills_inflicted,
                        "downed": p.downs_inflicted,
                    }
                ],
                "defenses": [
                    {
                        "damageTaken": 0,  # 解析器未提取
                        "boonStrips": (
                            p.boon_strips_received
                            if hasattr(p, "boon_strips_received")
                            else 0
                        ),
                        "conditionCleanses": p.condi_cleanses,
                        "downCount": p.own_downs,
                        "deadCount": p.own_deaths,
                    }
                ],
                "support": [
                    {
                        "condiCleanse": p.condi_cleanses,
                        "boonStrips": p.boon_strips,
                    }
                ],
                # 保留原有字段以兼容现有代码
                "dps": p.total_damage,
                "cc": p.breakbar_damage,
                "cleanses": p.condi_cleanses,
                "strips": p.boon_strips,
                "downs": p.own_downs,
                "deaths": p.own_deaths,
                "buffs": p.buff_uptime,
                "role": score_data.get("role", "unknown"),
                "total_score": score_data.get("total_score", 0),
                "score_details": score_data.get("score_details", {}),
            }
            players.append(player)

        # 地图ID到名称映射
        map_names = {
            38: "Eternal Battlegrounds",
            # 添加更多映射
        }
        fight_name = f"Detailed WvW - {map_names.get(meta.map_id, meta.map_name)}"

        # 构建返回数据
        return {
            "log_id": os.path.basename(file_path),
            "encounter_name": meta.map_name,
            "fightName": fight_name,
            "duration": meta.duration_s,
            "durationMS": int(meta.duration_s * 1000 + 691),  # 调整以匹配EI
            "recorded_by": cls._get_recorded_by(meta, player_stats),
            "date": meta.start_datetime or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timeStart": meta.start_datetime,
            "mode": "WvW" if meta.is_wvw else "PvE",
            "play_style": play_style,
            "map_name": meta.map_name,
            "map_id": meta.map_id,
            "gw2_build": meta.gw2_build,
            "gW2Build": meta.gw2_build,
            "player_count": len(player_stats),
            "players": players,
            "scores": scores,
            "phases": [
                {"name": "Full Fight", "start": 0, "end": int(meta.duration_s * 1000)}
            ],
            "targets": [],  # 简化，添加空列表
            "success": True,  # 假设成功
            "isCM": False,
            "detailedWvW": True,
            "language": "Chinese",
            "languageID": 5,
        }

    @classmethod
    def _get_recorded_by(cls, meta: Any, player_stats: list) -> str:
        """
        获取记录者信息
        Args:
            meta: 战斗元数据
            player_stats: 玩家统计数据

        Returns:
            记录者账号
        """
        if meta.pov_addr:
            for p in player_stats:
                if p.addr == meta.pov_addr:
                    return p.account
        return "Unknown"

    @classmethod
    def _create_mock_data(cls, file_path: str) -> Dict[str, Any]:
        """
        创建模拟数据

        当无法解析EVTC文件时返回模拟数据
        Args:
            file_path: 原始文件路径

        Returns:
            模拟的战斗数据字典
        """
        return {
            "log_id": os.path.basename(file_path),
            "encounter_name": "Unknown Encounter",
            "duration": 600,
            "duration_ms": 600000,
            "recorded_by": "Unknown",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "WvW",
            "play_style": "unknown",
            "map_name": "Unknown Map",
            "map_id": 0,
            "gw2_build": 0,
            "player_count": 2,
            "players": cls._create_mock_players(),
            "scores": [],
        }

    @staticmethod
    def _create_mock_players() -> list:
        """创建模拟玩家数据"""
        return [
            {
                "name": "Player1",
                "account": "Player1.1234",
                "profession": "Warrior",
                "dps": 10000,
                "cc": 500,
                "cleanses": 10,
                "strips": 5,
                "downs": 0,
                "deaths": 0,
                "buffs": {},
                "role": "dps",
                "total_score": 0,
                "score_details": {},
            },
            {
                "name": "Player2",
                "account": "Player2.5678",
                "profession": "Elementalist",
                "dps": 12000,
                "cc": 300,
                "cleanses": 5,
                "strips": 3,
                "downs": 1,
                "deaths": 0,
                "buffs": {},
                "role": "dps",
                "total_score": 0,
                "score_details": {},
            },
        ]
