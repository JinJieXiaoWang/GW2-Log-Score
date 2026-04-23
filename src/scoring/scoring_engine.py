"""
GW2战斗评分引擎主模块

提供统一的评分计算接口，支持多种游戏模式
"""

from typing import Dict, List, Any, Optional
from src.scoring.base_scorer import BaseScorer
from src.scoring.pve_scorer import PVEScorer
from src.scoring.wvw_scorer import WvWScorer
from src.scoring.survival_calculator import SurvivalCalculator
from src.scoring.role_detector import RoleDetector
from src.config import SCORING_CONFIG


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

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化评分引擎

        Args:
            config: 可选的评分配置，如不提供则使用默认配置
        """
        self.config = config or SCORING_CONFIG
        self._pve_scorer = PVEScorer(self.config)
        self._wvw_scorer = WvWScorer(self.config)

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
        """
        mode = parsed_data.get('mode', 'PVE-Other')

        if 'WvW' in mode:
            return self.calculate_wvw_scores(parsed_data)

        return self.calculate_pve_scores(parsed_data)

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
        """
        return self._pve_scorer.calculate(parsed_data)

    def calculate_wvw_scores(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        WvW模式评分计算

        评分维度:
        - DPS角色: DPS(60%) + Downs(20%) + Survival(20%)
        - SUPPORT角色: 稳固(20%) + 抗性(15%) + 急速(15%) + 清洁(20%) + 剥离(20%) + 生存(10%)
        - UTILITY角色: 剥离(30%) + 清洁(30%) + CC(20%) + 生存(20%)

        特殊规则:
        - 毒瘤小队(≤20人): DPS权重调整为 DPS(80%) + Downs(10%) + Survival(10%)

        Args:
            parsed_data: 解析后的WvW战斗数据

        Returns:
            玩家评分列表
        """
        return self._wvw_scorer.calculate(parsed_data)

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

    def _is_support(self, player: Dict[str, Any]) -> bool:
        """
        判断玩家是否为辅助角色

        代理方法，调用RoleDetector

        Args:
            player: 玩家数据字典

        Returns:
            True表示辅助角色，False表示其他
        """
        return RoleDetector.is_support(player)

    @staticmethod
    def get_player_role(player: Dict[str, Any]) -> str:
        """
        获取玩家角色定位

        Args:
            player: 玩家数据字典

        Returns:
            角色定位字符串 (DPS/SUPPORT/UTILITY)
        """
        return RoleDetector.detect(player)

    @staticmethod
    def get_survival_grade(score: float) -> str:
        """
        获取生存评分等级

        Args:
            score: 生存评分

        Returns:
            等级字符串 (S/A/B/C/D/F)
        """
        return SurvivalCalculator.get_grade(score)
