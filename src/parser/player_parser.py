"""
玩家数据解析模块

从日志数据中提取和标准化玩家信息
"""

from typing import Dict, Any, List, Optional
from src.core.logger import Logger

logger = Logger(__name__)


class PlayerParser:
    """
    玩家数据解析器

    负责从EI导出的JSON数据中提取玩家战斗数据
    """

    @classmethod
    def parse(cls, player_data: Dict[str, Any], duration_seconds: float) -> Dict[str, Any]:
        """
        解析单个玩家数据

        Args:
            player_data: EI格式的玩家数据
            duration_seconds: 战斗时长(秒)

        Returns:
            标准化后的玩家数据字典
        """
        return {
            'name': cls._get_name(player_data),
            'account': cls._get_account(player_data),
            'profession': cls._get_profession(player_data),
            'dps': cls._get_dps(player_data),
            'cc': cls._get_cc(player_data),
            'cleanses': cls._get_cleanses(player_data),
            'strips': cls._get_strips(player_data),
            'downs': cls._get_downs(player_data),
            'deaths': cls._get_deaths(player_data),
            'buffs': cls._get_buffs(player_data)
        }

    @classmethod
    def parse_all(cls, players_data: List[Dict[str, Any]], duration_seconds: float) -> List[Dict[str, Any]]:
        """
        解析所有玩家数据

        Args:
            players_data: EI格式的玩家数据列表
            duration_seconds: 战斗时长(秒)

        Returns:
            标准化后的玩家数据列表
        """
        return [cls.parse(p, duration_seconds) for p in players_data]

    @staticmethod
    def _get_name(data: Dict[str, Any]) -> str:
        """获取玩家名称"""
        return data.get('name', 'Unknown')

    @staticmethod
    def _get_account(data: Dict[str, Any]) -> str:
        """获取账户名"""
        return data.get('account', 'Unknown')

    @staticmethod
    def _get_profession(data: Dict[str, Any]) -> str:
        """获取职业"""
        return data.get('profession', 'Unknown')

    @staticmethod
    def _get_dps(data: Dict[str, Any]) -> int:
        """
        获取DPS数据

        从dpsAll数组的第一个元素获取DPS值
        """
        dps_stats = data.get('dpsAll', [{}])
        if dps_stats:
            return dps_stats[0].get('dps', 0)
        return 0

    @staticmethod
    def _get_cc(data: Dict[str, Any]) -> int:
        """
        获取破控伤害

        从dpsAll数组的第一个元素获取breakbarDamage值
        """
        dps_all = data.get('dpsAll', [{}])
        if dps_all:
            return dps_all[0].get('breakbarDamage', 0)
        return 0

    @staticmethod
    def _get_cleanses(data: Dict[str, Any]) -> int:
        """
        获取症状清洁次数

        包括对队友的清洁和自我清洁
        """
        support_list = data.get('support', [{}])
        if support_list:
            support = support_list[0]
            return support.get('condiCleanse', 0) + support.get('condiCleanseSelf', 0)
        return 0

    @staticmethod
    def _get_strips(data: Dict[str, Any]) -> int:
        """获取增益剥离次数"""
        support_list = data.get('support', [{}])
        if support_list:
            return support_list[0].get('boonStrips', 0)
        return 0

    @staticmethod
    def _get_downs(data: Dict[str, Any]) -> int:
        """获取倒地次数"""
        defenses_list = data.get('defenses', [{}])
        if defenses_list:
            return defenses_list[0].get('downCount', 0)
        return 0

    @staticmethod
    def _get_deaths(data: Dict[str, Any]) -> int:
        """获取死亡次数"""
        defenses_list = data.get('defenses', [{}])
        if defenses_list:
            return defenses_list[0].get('deadCount', 0)
        return 0

    @staticmethod
    def _get_buffs(data: Dict[str, Any]) -> Dict[int, float]:
        """
        获取增益覆盖率数据

        Returns:
            增益ID到覆盖率的映射字典
        """
        buff_uptimes = data.get('buffUptimes', [])
        buff_data = {}

        for buff in buff_uptimes:
            buff_id = buff.get('id')
            buff_stats_list = buff.get('buffData', [])

            if buff_id is not None and buff_stats_list:
                buff_data[buff_id] = buff_stats_list[0].get('uptime', 0)

        return buff_data
