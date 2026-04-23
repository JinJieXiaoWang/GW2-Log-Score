"""
PVE模式评分模块

计算PVE模式下的玩家评分
"""

from typing import Dict, List, Any, Optional
from src.scoring.base_scorer import BaseScorer, MetricsCalculator
from src.scoring.survival_calculator import SurvivalCalculator
from src.scoring.role_detector import RoleDetector
from src.config import BUFF_IDS


class PVEScorer(BaseScorer):
    """
    PVE模式评分器

    评分维度:
    - DPS角色: DPS(40%) + CC(35%) + Survival(25%)
    - SUPPORT角色: 稳固(35%) + 抗性(35%) + 增益(30%)
    """

    def calculate(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        计算PVE评分

        Args:
            parsed_data: 解析后的战斗数据

        Returns:
            玩家评分列表
        """
        players = parsed_data.get('players', [])
        if not players:
            return []

        averages = MetricsCalculator.calculate_all_averages(
            players,
            parsed_data.get('duration', 1)
        )

        scores = []
        for player in players:
            score_result = self._calculate_player_score(player, averages)
            scores.append(score_result)

        return scores

    def _calculate_player_score(
        self,
        player: Dict[str, Any],
        averages: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        计算单个玩家的PVE评分

        Args:
            player: 玩家数据
            averages: 团队平均值

        Returns:
            玩家评分结果
        """
        role = RoleDetector.detect(player)

        if role == 'SUPPORT':
            return self._calculate_support_score(player)
        else:
            return self._calculate_dps_score(player, averages)

    def _calculate_dps_score(
        self,
        player: Dict[str, Any],
        averages: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        计算DPS角色评分

        Args:
            player: 玩家数据
            averages: 团队平均值

        Returns:
            评分结果
        """
        weights = self.config['PVE']['DPS']['weights']

        dps = player.get('dps', 0)
        cc = player.get('cc', 0)

        s_dps = self.clamp(self.safe_divide(dps * 100, averages['avg_dps']))
        s_cc = self.clamp(self.safe_divide(cc * 100, averages['avg_cc']))
        s_survival = SurvivalCalculator.calculate_from_player(player)

        total_score = (
            s_dps * weights['dps'] +
            s_cc * weights['cc'] +
            s_survival * weights['survival']
        )

        return {
            'player_name': player['name'],
            'account': player.get('account', player['name']),
            'profession': player['profession'],
            'role': 'DPS',
            'scores': {
                'dps': round(s_dps, 2),
                'cc': round(s_cc, 2),
                'survival': round(s_survival, 2)
            },
            'total_score': round(total_score, 2),
            'details': {
                'dps_val': dps,
                'cc_val': cc,
                'downs': player.get('downs', 0),
                'deaths': player.get('deaths', 0)
            }
        }

    def _calculate_support_score(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算SUPPORT角色评分

        Args:
            player: 玩家数据

        Returns:
            评分结果
        """
        weights = self.config['PVE']['SUPPORT']['weights']

        buffs = player.get('buffs', {})

        s_stab = self.get_buff_uptime(buffs, '稳固')
        s_res = self.get_buff_uptime(buffs, '抗性')
        s_quick = self.get_buff_uptime(buffs, '急速')
        s_alac = self.get_buff_uptime(buffs, '敏捷')

        s_boon = max(s_quick, s_alac)

        total_score = (
            s_stab * weights['stability'] +
            s_res * weights['resistance'] +
            s_boon * weights['boon']
        )

        return {
            'player_name': player['name'],
            'account': player.get('account', player['name']),
            'profession': player['profession'],
            'role': 'SUPPORT',
            'scores': {
                'stability': round(s_stab, 2),
                'resistance': round(s_res, 2),
                'boon': round(s_boon, 2)
            },
            'total_score': round(total_score, 2),
            'details': {
                'stab_uptime': s_stab,
                'res_uptime': s_res,
                'quick_uptime': s_quick,
                'alac_uptime': s_alac
            }
        }
