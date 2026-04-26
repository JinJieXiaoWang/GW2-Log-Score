#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GW2战斗评分引擎主模块
提供统一的评分计算接口，支持多种游戏模式
"""

from typing import Dict, List, Any, Optional
from app.scoring.pve_scorer import PVEScorer
from app.scoring.wvw_scorer import WvWScorer
from app.scoring.wvw_rule_scorer import WvWRuleScorer, wvw_rule_scorer
from app.scoring.survival_calculator import SurvivalCalculator
from app.scoring.role_detector import RoleDetector
from app.config.config_loader import config_loader


class ScoringEngine:
    """
    GW2战斗评分引擎

    根据游戏模式(PVE/WvW)和玩家角色定位(DPS/SUPPORT/UTILITY)计算评分
    评分采用归一化算法，将个人数据与团队平均值对比得出相对得分(0-100)

    使用示例:
        engine = ScoringEngine()
        scores = engine.calculate_scores(parsed_data)
        for score in scores:
            print(f"{score['player_name']}: {score['total_score']}")
    """

    def __init__(self, config: Optional[Dict] = None, use_rule_based: bool = True):
        """
        初始化评分引擎
        Args:
            config: 可选的评分配置，如不提供则使用默认配置
            use_rule_based: 是否使用基于规则的评分器（默认True）

        Raises:
            ValueError: 配置无效
        """
        try:
            self.config = config or config_loader.get_scoring_all_rules()
            if not isinstance(self.config, dict):
                raise ValueError("Invalid configuration format")
            self._pve_scorer = PVEScorer(self.config)
            self._wvw_scorer = WvWScorer(self.config)
            self._wvw_rule_scorer = wvw_rule_scorer
            self._use_rule_based = use_rule_based
        except Exception as e:
            raise ValueError(f"Failed to initialize scoring engine: {e}")

    def calculate_scores(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据游戏模式分发到对应的评分计算函数

        Args:
            parsed_data: 解析后的战斗数据

        Returns:
            玩家评分列表，每个元素包含:
            - player_name: 玩家名称
            - account: 账户名
            - profession: 职业
            - role: 角色定位
            - scores: 各项得分
            - total_score: 总分
            - details: 详细信息

        Raises:
            ValueError: 数据格式无效
        """
        try:
            if not isinstance(parsed_data, dict):
                raise ValueError("Invalid parsed data format")

            mode = parsed_data.get("mode", "WvW")

            if "WvW" in mode:
                return self.calculate_wvw_scores(parsed_data)

            # 如果不是 WvW，暂时返回空的评分结果或者使用简单处理
            return self._fallback_calculate(parsed_data)
        except Exception as e:
            raise ValueError(f"Failed to calculate scores: {e}")

    def calculate_pve_scores(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        PVE模式评分计算

        评分维度:
        - DPS角色: DPS(40%) + CC(35%) + Survival(25%)
        - SUPPORT角色: 稳固(35%) + 抗性(35%) + 增益(30%)

        Args:
            parsed_data: 解析后的PVE战斗数据

        Returns:
            玩家评分列表

        Raises:
            ValueError: 数据格式无效
        """
        try:
            if not isinstance(parsed_data, dict):
                raise ValueError("Invalid parsed data format")
            return self._pve_scorer.calculate(parsed_data)
        except Exception as e:
            raise ValueError(f"Failed to calculate PVE scores: {e}")

    def calculate_wvw_scores(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        WvW模式评分计算

        评分维度:
        - DPS角色: DPS(60%) + Downs(20%) + Survival(20%)
        - SUPPORT角色: 稳固(20%) + 抗性(15%) + 急速(15%) + 清洁(20%) + 剥离(20%) + 生存(10%)
        - UTILITY角色: 剥离(30%) + 清洁(30%) + CC(20%) + 生存(20%)

        特殊规则:
        - 毒瘤小队(10人): DPS权重调整为DPS(80%) + Downs(10%) + Survival(10%)

        当use_rule_based=True 时，使用基于配置文件的职业/专精级别评分规则

        Args:
            parsed_data: 解析后的WvW战斗数据

        Returns:
            玩家评分列表

        Raises:
            ValueError: 数据格式无效
        """
        try:
            if not isinstance(parsed_data, dict):
                raise ValueError("Invalid parsed data format")
            if self._use_rule_based:
                return self._wvw_rule_scorer.calculate(parsed_data)
            return self._wvw_scorer.calculate(parsed_data)
        except Exception as e:
            raise ValueError(f"Failed to calculate WvW scores: {e}")

    def _calculate_survival_score(self, downs: int, deaths: int) -> float:
        """
        计算生存评分

        代理方法，调用SurvivalCalculator

        Args:
            downs: 倒地次数
            deaths: 死亡次数

        Returns:
            生存评分 (0-100)
        """
        return SurvivalCalculator.calculate(downs, deaths)

    def _fallback_calculate(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        备用评分计算方法，对于非 WvW 模式使用

        Args:
            parsed_data: 解析后的战斗数据

        Returns:
            简单的评分列表
        """
        try:
            scores = []
            if not isinstance(parsed_data, dict):
                return scores
            for p in parsed_data.get("players", []):
                if not isinstance(p, dict):
                    continue
                scores.append(
                    {
                        "player_name": p.get("name", "Unknown"),
                        "name": p.get("name", "Unknown"),
                        "account": p.get("account", "Unknown"),
                        "profession": p.get("profession", "Unknown"),
                        "role": p.get("role", "unknown"),
                        "total_score": 0,
                        "scores": {},
                        "details": {},
                    }
                )
            return scores
        except Exception:
            return []

    def _is_support(self, player: Dict[str, Any]) -> bool:
        """
        判断玩家是否为辅助角色
        代理方法，调用RoleDetector

        Args:
            player: 玩家数据字典

        Returns:
            True表示辅助角色，False表示其他
        """
        try:
            if not isinstance(player, dict):
                return False
            return RoleDetector.is_support(player)
        except Exception:
            return False

    @staticmethod
    def get_player_role(player: Dict[str, Any]) -> str:
        """
        获取玩家角色定位

        Args:
            player: 玩家数据字典

        Returns:
            角色定位字符串(DPS/SUPPORT/UTILITY)
        """
        try:
            if not isinstance(player, dict):
                return "DPS"
            return RoleDetector.detect(player)
        except Exception:
            return "DPS"

    @staticmethod
    def get_survival_grade(score: float) -> str:
        """
        获取生存评分等级

        Args:
            score: 生存评分

        Returns:
            等级字符串(S/A/B/C/D/F)
        """
        try:
            if not isinstance(score, (int, float)):
                return "F"
            return SurvivalCalculator.get_grade(score)
        except Exception:
            return "F"
