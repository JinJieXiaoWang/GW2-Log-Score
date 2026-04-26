#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生存评分计算模块

计算玩家的生存评分，基于倒地和死亡次数
"""

from typing import Dict, Any


class SurvivalCalculator:
    """
    生存评分计算器
    评分机制:
    - 基础分: 100分
    - 每次倒地: -20分
    - 每次死亡: -50分
    - 最低分: 0分
    """

    BASE_SCORE = 100
    PENALTY_PER_DOWN = 20
    PENALTY_PER_DEATH = 50

    @classmethod
    def calculate(cls, downs: int, deaths: int) -> float:
        """
        计算生存评分

        Args:
            downs: 倒地次数
            deaths: 死亡次数

        Returns:
            生存评分 (0-100)
        """
        penalty = (downs * cls.PENALTY_PER_DOWN) + (deaths * cls.PENALTY_PER_DEATH)
        score = cls.BASE_SCORE - penalty
        return max(0.0, score)

    @classmethod
    def calculate_from_player(cls, player: Dict[str, Any]) -> float:
        """
        从玩家数据计算生存评分
        Args:
            player: 玩家数据字典

        Returns:
            生存评分 (0-100)
        """
        downs = player.get("downs", 0)
        deaths = player.get("deaths", 0)
        return cls.calculate(downs, deaths)

    @classmethod
    def get_grade(cls, score: float) -> str:
        """
        根据评分获取等级

        Args:
            score: 生存评分

        Returns:
            等级字符串(S/A/B/C/D/F)
        """
        if score >= 100:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 40:
            return "C"
        elif score >= 20:
            return "D"
        else:
            return "F"

    @classmethod
    def get_description(cls, score: float) -> str:
        """
        获取评分描述

        Args:
            score: 生存评分

        Returns:
            评分描述
        """
        grade = cls.get_grade(score)
        descriptions = {
            "S": "完美生存，无倒地无死亡",
            "A": "优秀生存，极少失误",
            "B": "良好生存，有少量失误",
            "C": "一般生存，需要改进",
            "D": "较差生存，频繁失误",
            "F": "生存能力严重不足",
        }
        return descriptions.get(grade, "未知")
