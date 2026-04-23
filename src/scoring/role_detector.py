"""
玩家角色定位检测模块

根据职业和Buff数据判断玩家的角色定位(DPS/SUPPORT/UTILITY)
"""

from typing import Dict, Any, Optional
from src.config import PROF_ROLES, BUFF_IDS


class RoleDetector:
    """
    玩家角色定位检测器

    角色类型:
    - DPS: 伤害输出者
    - SUPPORT: 辅助职业(提供急速/敏捷/稳固/抗性等)
    - UTILITY: 功能性职业(清洁/剥离)
    """

    SUPPORT_BUFF_THRESHOLD = 50

    @classmethod
    def detect(cls, player: Dict[str, Any]) -> str:
        """
        检测玩家角色定位

        检测优先级:
        1. 配置文件中的职业-角色映射
        2. 基于Buff覆盖率的推断

        Args:
            player: 玩家数据字典

        Returns:
            角色定位字符串 (DPS/SUPPORT/UTILITY)
        """
        profession = player.get('profession', '')

        if profession in PROF_ROLES:
            return PROF_ROLES[profession]

        return cls._infer_from_buffs(player)

    @classmethod
    def _infer_from_buffs(cls, player: Dict[str, Any]) -> str:
        """
        从Buff数据推断角色定位

        Args:
            player: 玩家数据字典

        Returns:
            推断的角色定位
        """
        buffs = player.get('buffs', {})

        quick_uptime = cls._get_buff_uptime(buffs, '急速')
        alac_uptime = cls._get_buff_uptime(buffs, '敏捷')
        stab_uptime = cls._get_buff_uptime(buffs, '稳固')

        if quick_uptime > cls.SUPPORT_BUFF_THRESHOLD:
            return 'SUPPORT'

        if alac_uptime > cls.SUPPORT_BUFF_THRESHOLD:
            return 'SUPPORT'

        if stab_uptime > cls.SUPPORT_BUFF_THRESHOLD:
            return 'SUPPORT'

        cleanses = player.get('cleanses', 0)
        strips = player.get('strips', 0)

        if cleanses > 10 or strips > 10:
            return 'UTILITY'

        return 'DPS'

    @classmethod
    def _get_buff_uptime(cls, buffs: Dict[int, float], buff_name: str) -> float:
        """
        获取指定增益的覆盖率

        Args:
            buffs: 增益数据字典
            buff_name: 增益名称

        Returns:
            增益覆盖率
        """
        buff_id = BUFF_IDS.get(buff_name, 0)
        return buffs.get(buff_id, 0)

    @classmethod
    def is_support(cls, player: Dict[str, Any]) -> bool:
        """
        判断玩家是否为辅助角色

        Args:
            player: 玩家数据字典

        Returns:
            是否为辅助角色
        """
        return cls.detect(player) == 'SUPPORT'

    @classmethod
    def is_dps(cls, player: Dict[str, Any]) -> bool:
        """
        判断玩家是否为DPS角色

        Args:
            player: 玩家数据字典

        Returns:
            是否为DPS角色
        """
        return cls.detect(player) == 'DPS'

    @classmethod
    def is_utility(cls, player: Dict[str, Any]) -> bool:
        """
        判断玩家是否为功能性角色

        Args:
            player: 玩家数据字典

        Returns:
            是否为功能性角色
        """
        return cls.detect(player) == 'UTILITY'
