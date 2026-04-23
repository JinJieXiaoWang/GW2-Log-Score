"""
评分计算基础模块

提供评分计算的通用工具和基类
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from src.config import SCORING_CONFIG, BUFF_IDS, PROF_ROLES


class BaseScorer(ABC):
    """
    评分器基类

    所有评分器都应继承此类并实现calculate方法
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化评分器

        Args:
            config: 可选的评分配置
        """
        self.config = config or SCORING_CONFIG

    @abstractmethod
    def calculate(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        计算评分

        Args:
            parsed_data: 解析后的战斗数据

        Returns:
            玩家评分列表
        """
        pass

    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        安全除法，避免除零错误

        Args:
            numerator: 被除数
            denominator: 除数
            default: 除数为零时的默认返回值

        Returns:
            除法结果或默认值
        """
        if denominator == 0:
            return default
        return numerator / denominator

    @staticmethod
    def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """
        将值限制在指定范围内

        Args:
            value: 待限制的值
            min_val: 最小值
            max_val: 最大值

        Returns:
            限制后的值
        """
        return max(min_val, min(max_val, value))

    @staticmethod
    def get_buff_uptime(buffs: Dict[int, float], buff_name: str) -> float:
        """
        获取指定增益的覆盖率

        Args:
            buffs: 增益数据字典
            buff_name: 增益名称(中文)

        Returns:
            增益覆盖率(0-100)
        """
        buff_id = BUFF_IDS.get(buff_name, 0)
        return buffs.get(buff_id, 0)


class MetricsCalculator:
    """
    指标计算工具类

    提供各种战斗指标的计算方法
    """

    @staticmethod
    def calculate_team_average(players: List[Dict[str, Any]], key: str) -> float:
        """
        计算团队某项指标的平均值

        Args:
            players: 玩家数据列表
            key: 指标键名

        Returns:
            平均值，无玩家时返回0
        """
        if not players:
            return 0
        total = sum(p.get(key, 0) for p in players)
        return total / len(players)

    @staticmethod
    def calculate_per_minute(value: float, duration_seconds: float) -> float:
        """
        计算每分钟指标

        Args:
            value: 总值
            duration_seconds: 持续时间(秒)

        Returns:
            每分钟值
        """
        if duration_seconds <= 0:
            return 0
        return value / (duration_seconds / 60)

    @classmethod
    def calculate_all_averages(
        cls,
        players: List[Dict[str, Any]],
        duration_seconds: float
    ) -> Dict[str, float]:
        """
        计算所有常用团队平均值

        Args:
            players: 玩家数据列表
            duration_seconds: 战斗时长(秒)

        Returns:
            包含各项平均值的字典
        """
        duration_min = duration_seconds / 60 if duration_seconds > 0 else 1

        return {
            'avg_dps': max(1, cls.calculate_team_average(players, 'dps')),
            'avg_cc': max(1, cls.calculate_team_average(players, 'cc')),
            'avg_cleanses_per_min': max(1, cls.calculate_team_average(
                [{'cleanses_per_min': p.get('cleanses', 0) / duration_min} for p in players],
                'cleanses_per_min'
            )),
            'avg_strips_per_min': max(1, cls.calculate_team_average(
                [{'strips_per_min': p.get('strips', 0) / duration_min} for p in players],
                'strips_per_min'
            )),
            'avg_cc_per_min': max(1, cls.calculate_team_average(
                [{'cc_per_min': p.get('cc', 0) / duration_min} for p in players],
                'cc_per_min'
            )),
            'avg_downs': max(1, cls.calculate_team_average(players, 'downs')),
            'avg_deaths': max(1, cls.calculate_team_average(players, 'deaths')),
        }
