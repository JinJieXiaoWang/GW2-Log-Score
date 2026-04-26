#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WvW模式评分模块 v2 - 基于规则配置

支持职业-专精级别的详细评分规则配置
"""

import re
from typing import Dict, List, Any, Optional
from app.scoring.base_scorer import BaseScorer, MetricsCalculator
from app.scoring.survival_calculator import SurvivalCalculator
from app.scoring.role_detector import RoleDetector
from app.config.config_loader import config_loader


class WvWRuleScorer(BaseScorer):
    """
    WvW模式规则评分器
    支持从配置文件加载职业-专精级别的详细评分规则
    """

    SMALL_SQUAD_THRESHOLD = 20

    # Buff ID 映射
    BUFF_ID_MAP = {
        "Stability": 1122,
        "Resistance": 4614,
        "Swiftness": 1187,
        "Regeneration": 30328,
        "Protection": 717,
        "Vigor": 30333,
    }

    def __init__(self):
        """
        初始化WvW规则评分器

        Raises:
            ValueError: 配置加载失败
        """
        try:
            super().__init__(config_loader.scoring_rules_config)
            # 从配置加载器获取配置
            self.dimension_definitions = config_loader.get_scoring_dimension_definitions()
            self.squad_size_rules = config_loader.get_scoring_squad_size_rules()
            self.profession_specialization_rules = (
                config_loader.get_scoring_profession_specialization_rules()
            )
            self.fallback_role_rules = config_loader.get_scoring_fallback_role_rules()
        except Exception as e:
            raise ValueError(f"Failed to initialize WvW rule scorer: {e}")

    def calculate(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        计算WvW评分

        Args:
            parsed_data: 解析后的战斗数据

        Returns:
            玩家评分列表

        Raises:
            ValueError: 数据格式无效
        """
        try:
            if not isinstance(parsed_data, dict):
                raise ValueError("Invalid parsed data format")

            players = parsed_data.get("players", [])
            duration_s = parsed_data.get("duration", 1)

            if not players:
                return []

            is_small_squad = len(players) <= self.SMALL_SQUAD_THRESHOLD
            averages = MetricsCalculator.calculate_all_averages(players, duration_s)
            duration_min = duration_s / 60 if duration_s > 0 else 1

            scores = []
            for player in players:
                try:
                    score_result = self._calculate_player_score(
                        player, averages, duration_min, is_small_squad
                    )
                    scores.append(score_result)
                except Exception as e:
                    # 记录错误并继续处理其他玩家
                    continue

            return scores
        except Exception as e:
            raise ValueError(f"Failed to calculate WvW scores: {e}")

    def _calculate_player_score(
        self,
        player: Dict[str, Any],
        averages: Dict[str, float],
        duration_min: float,
        is_small_squad: bool,
    ) -> Dict[str, Any]:
        """
        计算单个玩家的WvW评分

        Args:
            player: 玩家数据
            averages: 团队平均值
            duration_min: 战斗时长(分钟)
            is_small_squad: 是否为毒瘤小队
        Returns:
            评分结果
        """
        profession = player.get("profession", "Unknown")
        specialization = player.get("specialization", profession)
        stance = player.get("stance")
        weapon = player.get("weapon")
        role = RoleDetector.detect(player)

        rule = self._get_scoring_rule(profession, specialization, stance, weapon, role)

        if not rule:
            return self._create_default_score(player, role)

        dimension_weights = rule.get("dimension_weights", {})
        data_sources = rule.get("data_sources", {})

        if is_small_squad:
            dimension_weights = self._apply_small_squad_modifiers(
                dimension_weights, role
            )

        scores = {}
        raw_values = {}
        total_score = 0

        for dimension, weight in dimension_weights.items():
            value = self._calculate_dimension_score(
                dimension, player, averages, duration_min, data_sources
            )
            normalized_value = self.clamp(value, 0, 100)
            scores[dimension] = round(normalized_value, 2)
            raw_values[dimension] = round(value, 2)
            total_score += normalized_value * (weight / 100)

        survival_score = SurvivalCalculator.calculate_from_player(player)
        if "survival_score" in dimension_weights:
            scores["survival_score"] = round(survival_score, 2)
            raw_values["survival_score"] = survival_score
            total_score += survival_score * (dimension_weights["survival_score"] / 100)

        return {
            "player_name": player.get("name", "Unknown"),
            "account": player.get("account", ""),
            "profession": profession,
            "specialization": specialization,
            "stance": stance,
            "weapon": weapon,
            "role": rule.get("role", role),
            "display_name": rule.get("display_name", f"{profession}-{specialization}"),
            "scores": scores,
            "raw_values": raw_values,
            "weights": dimension_weights,
            "total_score": round(total_score, 2),
            "details": {
                "team_size": "small_squad" if is_small_squad else "large_squad",
                "rule_type": rule.get("rule_type", "unknown"),
                "duration_min": round(duration_min, 2),
                "dimension_definitions": {
                    k: self.dimension_definitions.get(k, {})
                    for k in dimension_weights.keys()
                },
            },
        }

    def _get_scoring_rule(
        self,
        profession: str,
        specialization: str,
        stance: str = None,
        weapon: str = None,
        role: str = None,
    ) -> Optional[Dict[str, Any]]:
        """
        获取匹配的评分规则
        Args:
            profession: 职业名称
            specialization: 专精名称
            stance: 姿态（可选）
            weapon: 武器（可选）
            role: 角色定位

        Returns:
            匹配的评分规则，未找到则返回None
        """
        # 暂时返回默认规则
        return {
            "role": role,
            "dimension_weights": {"dps": 60, "downs": 20, "survival_score": 20},
            "data_sources": {"dps": "dps", "downs": "downs"},
        }

    def _apply_small_squad_modifiers(
        self, dimension_weights: Dict[str, float], role: str
    ) -> Dict[str, float]:
        """
        应用小团队权重调整
        Args:
            dimension_weights: 原始权重
            role: 角色定位

        Returns:
            调整后的权重
        """
        # 暂时返回原始权重
        return dimension_weights.copy()

    def _calculate_dimension_score(
        self,
        dimension: str,
        player: Dict[str, Any],
        averages: Dict[str, float],
        duration_min: float,
        data_sources: Dict[str, str],
    ) -> float:
        """
        计算单个维度的分数
        Args:
            dimension: 维度名称
            player: 玩家数据
            averages: 团队平均值
            duration_min: 战斗时长(分钟)
            data_sources: 数据源配置
        Returns:
            维度分数
        """
        if dimension == "survival_score":
            return SurvivalCalculator.calculate_from_player(player)

        data_source = data_sources.get(dimension, "")
        value = self._extract_value_from_player(
            player, data_source, duration_min, averages
        )

        if value is None:
            return 0

        norm_rule = self._get_normalization_rule(dimension)

        if norm_rule == "relative_to_average":
            avg_key = self._get_average_key(dimension)
            if avg_key in averages and averages.get(avg_key, 0) > 0:
                return (value / averages[avg_key]) * 100
            return 0

        elif norm_rule == "inverse_relative_to_average":
            avg_key = self._get_average_key(dimension)
            if avg_key in averages and value > 0:
                return min((averages[avg_key] / value) * 100, 100)
            return 0

        elif norm_rule == "percentage":
            return min(value, 100)

        else:
            return value

    def _extract_value_from_player(
        self,
        player: Dict[str, Any],
        data_source: str,
        duration_min: float,
        averages: Dict[str, float],
    ) -> Optional[float]:
        """
        从玩家数据中提取指定字段的值
        Args:
            player: 玩家数据
            data_source: 数据源描述
            duration_min: 战斗时长(分钟)
            averages: 团队平均值
        Returns:
            提取的值
        """
        if not data_source:
            return None

        # 处理计算表达式
        if "deaths" in data_source and "downs" in data_source:
            deaths = player.get("deaths", 0)
            downs = player.get("downs", 0)
            return max(0, 100 - (deaths * 20 + downs * 10))

        # 处理组合数据源
        if "+" in data_source:
            parts = data_source.split("+")
            total = 0
            for part in parts:
                part = part.strip()
                val = self._extract_single_value(player, part, duration_min)
                if val is not None:
                    total += val
            return total if total > 0 else None

        return self._extract_single_value(player, data_source, duration_min)

    def _extract_single_value(
        self, player: Dict[str, Any], field: str, duration_min: float
    ) -> Optional[float]:
        """
        提取单个字段的值
        Args:
            player: 玩家数据
            field: 字段名
            duration_min: 战斗时长(分钟)

        Returns:
            字段值
        """
        if field in ["deaths", "downs"]:
            return player.get(field, 0)

        # 伤害相关
        if field in [
            "damage_target",
            "damageTargetPerSecond",
            "damage_per_second",
            "dps",
        ]:
            return player.get(
                "dps",
                player.get("damageTargetPerSecond", player.get("damage_target", 0)),
            )

        if field == "damage_taken":
            return player.get("damage_taken", player.get("damageTaken", 0))

        if field == "healing_done":
            return player.get("healing_done", player.get("healingDone", 0))

        if field == "stripped_buffs":
            return player.get("strips", player.get("strippedBuffs", 0))

        if field == "breakbar_damage":
            return player.get(
                "cc", player.get("breakbarDamage", player.get("breakbar_damage", 0))
            )

        if field == "cleanses":
            return player.get("cleanses", 0)

        if field == "negated_attacks":
            return player.get("negated_attacks", player.get("negatedAttacks", 0))

        if field == "group_hit_efficiency":
            return player.get(
                "group_hit_efficiency", player.get("groupHitEfficiency", 0)
            )

        # Buff 覆盖率
        buff_match = re.match(
            r"buff_uptimes\[(\w+)\]", field, re.IGNORECASE
        ) or re.match(r"buffUptimes\[(\w+)\]", field)
        if buff_match:
            buff_name = buff_match.group(1)
            return self._get_buff_uptime(player, buff_name)

        # Debuff 覆盖率
        debuff_match = re.match(
            r"debuff_uptimes\[(\w+)\]", field, re.IGNORECASE
        ) or re.match(r"debuffUptimes\[(\w+)\]", field)
        if debuff_match:
            debuff_name = debuff_match.group(1)
            return self._get_debuff_uptime(player, debuff_name)

        # 每分钟统计
        if "_per_min" in field.lower() or "_per_minute" in field.lower():
            base_field = field.replace("_per_min", "").replace("_per_minute", "")
            base_value = player.get(base_field, 0)
            return base_value / duration_min if duration_min > 0 else 0

        return player.get(field, 0)

    def _get_buff_uptime(self, player: Dict[str, Any], buff_name: str) -> float:
        """
        获取增益覆盖率
        Args:
            player: 玩家数据
            buff_name: 增益名称

        Returns:
            覆盖率(0-100)
        """
        buffs = player.get("buffs", {})
        if not isinstance(buffs, dict):
            return 0

        # 尝试多种方式查找
        if isinstance(buffs, dict):
            buff_id = self.BUFF_ID_MAP.get(buff_name, None)
            if buff_id is not None and buff_id in buffs:
                return buffs[buff_id]

            for key in buffs.keys():
                if str(key).lower() == buff_name.lower():
                    return buffs[key]

        return 0

    def _get_debuff_uptime(self, player: Dict[str, Any], debuff_name: str) -> float:
        """
        获取减益覆盖率
        Args:
            player: 玩家数据
            debuff_name: 减益名称

        Returns:
            覆盖率(0-100)
        """
        debuffs = player.get("debuffs", {})
        if not isinstance(debuffs, dict):
            return 0

        if isinstance(debuffs, dict):
            for key in debuffs.keys():
                if str(key).lower() == debuff_name.lower():
                    return debuffs[key]

        return 0

    def _get_normalization_rule(self, dimension: str) -> str:
        """
        获取维度的标准化规则

        Args:
            dimension: 维度名称

        Returns:
            标准化规则名称
        """
        dim_def = self.dimension_definitions.get(dimension, {})
        return dim_def.get("normalization", "fixed")

    def _get_average_key(self, dimension: str) -> str:
        """
        获取维度对应的平均值键

        Args:
            dimension: 维度名称

        Returns:
            平均值键
        """
        mapping = {
            "cleanses": "avg_cleanses_per_min",
            "strips": "avg_strips_per_min",
            "breakbar_damage": "avg_cc",
            "healing_done": "avg_healing_done",
            "damage_taken": "avg_damage_taken",
            "damage_per_second": "avg_dps",
            "negated_attacks": "avg_negated_attacks",
        }
        return mapping.get(dimension, f"avg_{dimension}")

    def _create_default_score(
        self, player: Dict[str, Any], role: str
    ) -> Dict[str, Any]:
        """
        创建默认评分（当没有匹配规则时）

        Args:
            player: 玩家数据
            role: 角色定位

        Returns:
            默认评分结果
        """
        return {
            "player_name": player.get("name", "Unknown"),
            "account": player.get("account", ""),
            "profession": player.get("profession", "Unknown"),
            "specialization": player.get("specialization", ""),
            "stance": player.get("stance"),
            "weapon": player.get("weapon"),
            "role": role,
            "display_name": player.get("profession", "Unknown"),
            "scores": {},
            "raw_values": {},
            "weights": {},
            "total_score": 0,
            "details": {
                "team_size": "unknown",
                "rule_type": "none",
                "duration_min": 0,
            },
        }


wvw_rule_scorer = WvWRuleScorer()
