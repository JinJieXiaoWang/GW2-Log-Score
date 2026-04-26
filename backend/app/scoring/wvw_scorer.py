#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WvW模式评分模块

计算WvW模式下的玩家评分
"""

from typing import Dict, List, Any
from app.scoring.base_scorer import BaseScorer, MetricsCalculator
from app.scoring.survival_calculator import SurvivalCalculator
from app.scoring.role_detector import RoleDetector


class WvWScorer(BaseScorer):
    """
    WvW模式评分器
    评分维度:
    - DPS角色: DPS(60%) + Downs(20%) + Survival(20%)
    - SUPPORT角色: 稳固(20%) + 抗性(15%) + 急速(15%) + 清洁(20%) + 剥离(20%) + 生存(10%)
    - UTILITY角色: 剥离(30%) + 清洁(30%) + CC(20%) + 生存(20%)

    特殊规则:
    - 毒瘤小队(20人): DPS权重调整为DPS(80%) + Downs(10%) + Survival(10%)
    """

    SMALL_SQUAD_THRESHOLD = 20

    def calculate(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        计算WvW评分

        Args:
            parsed_data: 解析后的战斗数据

        Returns:
            玩家评分列表
        """
        players = parsed_data.get("players", [])
        duration_s = parsed_data.get("duration", 1)

        if not players:
            return []

        is_small_squad = len(players) <= self.SMALL_SQUAD_THRESHOLD
        averages = MetricsCalculator.calculate_all_averages(players, duration_s)
        duration_min = duration_s / 60 if duration_s > 0 else 1

        scores = []
        for player in players:
            role = RoleDetector.detect(player)
            score_result = self._calculate_player_score(
                player, role, averages, duration_min, is_small_squad
            )
            scores.append(score_result)

        return scores

    def _calculate_player_score(
        self,
        player: Dict[str, Any],
        role: str,
        averages: Dict[str, float],
        duration_min: float,
        is_small_squad: bool,
    ) -> Dict[str, Any]:
        """
        计算单个玩家的WvW评分

        Args:
            player: 玩家数据
            role: 角色定位
            averages: 团队平均值
            duration_min: 战斗时长(分钟)
            is_small_squad: 是否为毒瘤小队
        Returns:
            评分结果
        """
        if role == "DPS":
            return self._calculate_dps_score(player, averages, is_small_squad)
        elif role == "SUPPORT":
            return self._calculate_support_score(
                player, averages, duration_min, is_small_squad
            )
        else:
            return self._calculate_utility_score(
                player, averages, duration_min, is_small_squad
            )

    def _calculate_dps_score(
        self, player: Dict[str, Any], averages: Dict[str, float], is_small_squad: bool
    ) -> Dict[str, Any]:
        """
        计算DPS角色评分

        Args:
            player: 玩家数据
            averages: 团队平均值
            is_small_squad: 是否为毒瘤小队
        Returns:
            评分结果
        """
        if is_small_squad:
            weights = {"dps": 0.8, "downs": 0.1, "survival": 0.1}
        else:
            # 暂时使用默认权重，需要从配置中读取
            weights = {"dps": 0.6, "downs": 0.2, "survival": 0.2}

        dps = player.get("dps", 0)
        downs = player.get("downs", 0)

        s_dps = self.clamp(self.safe_divide(dps * 100, averages["avg_dps"]))
        s_downs = self.clamp(self.safe_divide(downs * 100, averages["avg_downs"]))
        s_survival = SurvivalCalculator.calculate_from_player(player)

        total_score = (
            s_dps * weights["dps"]
            + s_downs * weights["downs"]
            + s_survival * weights["survival"]
        )

        return {
            "player_name": player["name"],
            "account": player.get("account", player["name"]),
            "profession": player["profession"],
            "role": "DPS",
            "scores": {
                "dps": round(s_dps, 2),
                "downs": round(s_downs, 2),
                "survival": round(s_survival, 2),
            },
            "total_score": round(total_score, 2),
            "details": {
                "dps_val": dps,
                "downs_val": downs,
                "team_size": "small_squad" if is_small_squad else "large_squad",
            },
        }

    def _calculate_support_score(
        self,
        player: Dict[str, Any],
        averages: Dict[str, float],
        duration_min: float,
        is_small_squad: bool,
    ) -> Dict[str, Any]:
        """
        计算SUPPORT角色评分

        Args:
            player: 玩家数据
            averages: 团队平均值
            duration_min: 战斗时长(分钟)
            is_small_squad: 是否为毒瘤小队
        Returns:
            评分结果
        """
        # 暂时使用默认权重，需要从配置中读取
        weights = {
            "stability": 0.2,
            "resistance": 0.15,
            "quickness": 0.15,
            "cleanses": 0.2,
            "strips": 0.2,
            "survival": 0.1,
        }

        buffs = player.get("buffs", {})
        cleanses = player.get("cleanses", 0)
        strips = player.get("strips", 0)

        cleanses_per_min = cleanses / duration_min if duration_min > 0 else 0
        strips_per_min = strips / duration_min if duration_min > 0 else 0

        s_stab = self.get_buff_uptime(buffs, "稳固")
        s_res = self.get_buff_uptime(buffs, "抗性")
        s_quick = self.get_buff_uptime(buffs, "急速")
        s_cleanse = self.clamp(
            self.safe_divide(cleanses_per_min * 100, averages["avg_cleanses_per_min"])
        )
        s_strips = self.clamp(
            self.safe_divide(strips_per_min * 100, averages["avg_strips_per_min"])
        )
        s_survival = SurvivalCalculator.calculate_from_player(player)

        total_score = (
            s_stab * weights["stability"]
            + s_res * weights["resistance"]
            + s_quick * weights["quickness"]
            + s_cleanse * weights["cleanses"]
            + s_strips * weights["strips"]
            + s_survival * weights["survival"]
        )

        return {
            "player_name": player["name"],
            "account": player.get("account", player["name"]),
            "profession": player["profession"],
            "role": "SUPPORT",
            "scores": {
                "stability": round(s_stab, 2),
                "resistance": round(s_res, 2),
                "quickness": round(s_quick, 2),
                "cleanses": round(s_cleanse, 2),
                "strips": round(s_strips, 2),
                "survival": round(s_survival, 2),
            },
            "total_score": round(total_score, 2),
            "details": {
                "cleanses_per_min": round(cleanses_per_min, 2),
                "strips_per_min": round(strips_per_min, 2),
                "team_size": "small_squad" if is_small_squad else "large_squad",
            },
        }

    def _calculate_utility_score(
        self,
        player: Dict[str, Any],
        averages: Dict[str, float],
        duration_min: float,
        is_small_squad: bool,
    ) -> Dict[str, Any]:
        """
        计算UTILITY角色评分

        Args:
            player: 玩家数据
            averages: 团队平均值
            duration_min: 战斗时长(分钟)
            is_small_squad: 是否为毒瘤小队
        Returns:
            评分结果
        """
        # 暂时使用默认权重，需要从配置中读取
        weights = {"strips": 0.3, "cleanses": 0.3, "cc": 0.2, "survival": 0.2}

        cleanses = player.get("cleanses", 0)
        strips = player.get("strips", 0)
        cc = player.get("cc", 0)

        cleanses_per_min = cleanses / duration_min if duration_min > 0 else 0
        strips_per_min = strips / duration_min if duration_min > 0 else 0
        cc_per_min = cc / duration_min if duration_min > 0 else 0

        s_strips = self.clamp(
            self.safe_divide(strips_per_min * 100, averages["avg_strips_per_min"])
        )
        s_cleanse = self.clamp(
            self.safe_divide(cleanses_per_min * 100, averages["avg_cleanses_per_min"])
        )
        s_cc = self.clamp(cc_per_min)
        s_survival = SurvivalCalculator.calculate_from_player(player)

        total_score = (
            s_strips * weights["strips"]
            + s_cleanse * weights["cleanses"]
            + s_cc * weights["cc"]
            + s_survival * weights["survival"]
        )

        return {
            "player_name": player["name"],
            "account": player.get("account", player["name"]),
            "profession": player["profession"],
            "role": "UTILITY",
            "scores": {
                "strips": round(s_strips, 2),
                "cleanses": round(s_cleanse, 2),
                "cc": round(s_cc, 2),
                "survival": round(s_survival, 2),
            },
            "total_score": round(total_score, 2),
            "details": {
                "strips_per_min": round(strips_per_min, 2),
                "cleanses_per_min": round(cleanses_per_min, 2),
                "cc_per_min": round(cc_per_min, 2),
                "team_size": "small_squad" if is_small_squad else "large_squad",
            },
        }
