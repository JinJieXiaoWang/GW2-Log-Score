# -*- coding: utf-8 -*-
"""
游戏模式检测模块
根据日志数据自动检测游戏模式(PVE/WvW/PvP等)
"""

from typing import Dict, Any, List
from app.core.logger import Logger

logger = Logger(__name__)


class ModeDetector:
    """
    游戏模式检测器

    支持检测的游戏模式:
    - WvW: 世界之战
    - PvP: 玩家对战
    - PVE-Raid: 团队副本
    - PVE-Strike: 进攻任务
    - PVE-Fractal: 迷雾碎层
    - PVE-Other: 其他PVE内容
    """

    FRACTAL_KEYWORDS: List[str] = [
        "fractal",
        "nightmare",
        "shattered observatory",
        "sunqua peak",
        "silent surf",
        "lonely tower",
    ]

    RAID_KEYWORDS: List[str] = [
        "vale guardian",
        "gorseval",
        "sabetha",
        "slothasor",
        "matthias",
        "keep construct",
        "xera",
        "cairn",
        "mursaat overseer",
        "samarog",
        "deimos",
        "soulless horror",
        "river of souls",
        "statues of ice",
        "voice in the void",
        "conjured amalgamate",
        "twin largos",
        "qadim",
    ]

    STRIKE_KEYWORDS: List[str] = [
        "aetherblade hideout",
        "junkyard",
        "overlook",
        "harvest temple",
        "old lion",
        "cosmic observatory",
        "temple of febe",
    ]

    @classmethod
    def detect(cls, data: Dict[str, Any]) -> str:
        """
        检测游戏模式
        检测优先级:
        1. EI显式标记 (isWvW, isPvP, isRaid等)
        2. 基于战斗名称的关键词匹配

        Args:
            data: 解析后的JSON数据

        Returns:
            游戏模式字符串
        """
        mode = cls._check_explicit_flags(data)
        if mode:
            return mode

        mode = cls._check_keywords(data)
        if mode:
            return mode

        return cls._check_default(data)

    @classmethod
    def _check_explicit_flags(cls, data: Dict[str, Any]) -> str:
        """
        检查EI显式标记的模式标签
        Args:
            data: 解析后的JSON数据

        Returns:
            检测到的模式，未检测到返回空字符串
        """
        if data.get("isWvW") or data.get("detailedWvW"):
            return "WvW"

        if data.get("isPvP"):
            return "PvP"

        if data.get("isRaid"):
            return "PVE-Raid"

        if data.get("isStrike"):
            return "PVE-Strike"

        if data.get("isFractal"):
            return "PVE-Fractal"

        return ""

    @classmethod
    def _check_keywords(cls, data: Dict[str, Any]) -> str:
        """
        基于关键词检测游戏模式
        Args:
            data: 解析后的JSON数据

        Returns:
            检测到的模式，未检测到返回空字符串
        """
        name = cls._get_encounter_name(data).lower()

        if cls._contains_any(name, cls.FRACTAL_KEYWORDS):
            return "PVE-Fractal"

        if cls._contains_any(name, cls.RAID_KEYWORDS):
            return "PVE-Raid"

        if cls._contains_any(name, cls.STRIKE_KEYWORDS):
            return "PVE-Strike"

        return ""

    @classmethod
    def _check_default(cls, data: Dict[str, Any]) -> str:
        """
        默认模式检测逻辑

        Args:
            data: 解析后的JSON数据

        Returns:
            默认模式
        """
        name = cls._get_encounter_name(data).lower()

        if "wvw" in name or not data.get("targets"):
            return "WvW"

        # 默认返回 WvW
        return "WvW"

    @classmethod
    def _get_encounter_name(cls, data: Dict[str, Any]) -> str:
        """
        获取战斗名称

        Args:
            data: 解析后的JSON数据

        Returns:
            战斗名称
        """
        return data.get("fightName") or data.get("encounterName", "")

    @classmethod
    def _contains_any(cls, text: str, keywords: List[str]) -> bool:
        """
        检查文本是否包含任一关键词
        Args:
            text: 待检查文本
            keywords: 关键词列表
        Returns:
            是否包含任一关键词
        """
        return any(keyword in text for keyword in keywords)
