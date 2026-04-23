from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Player:
    """
    玩家数据模型

    Attributes:
        name: 玩家名称(主键)
        profession: 职业
        role: 角色定位 (DPS/SUPPORT/UTILITY)
        account: 账户名
    """
    name: str
    profession: str
    role: str = ''
    account: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'profession': self.profession,
            'role': self.role,
            'account': self.account
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        return cls(
            name=data.get('name', ''),
            profession=data.get('profession', ''),
            role=data.get('role', ''),
            account=data.get('account', '')
        )


@dataclass
class CombatLog:
    """
    战斗日志数据模型

    Attributes:
        log_id: 日志唯一标识
        mode: 游戏模式 (PVE-Raid/PVE-Strike/PVE-Fractal/WvW/PvP等)
        encounter_name: 战斗名称
        date: 战斗日期
        duration: 战斗时长(秒)
        log_path: 日志文件路径
        recorder: 记录者
    """
    log_id: str
    mode: str
    encounter_name: str
    date: str
    duration: int = 0
    log_path: str = ''
    recorder: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return {
            'log_id': self.log_id,
            'mode': self.mode,
            'encounter_name': self.encounter_name,
            'date': self.date,
            'duration': self.duration,
            'log_path': self.log_path,
            'recorder': self.recorder
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatLog':
        return cls(
            log_id=data.get('log_id', ''),
            mode=data.get('mode', ''),
            encounter_name=data.get('encounter_name', ''),
            date=data.get('date', ''),
            duration=data.get('duration', 0),
            log_path=data.get('log_path', ''),
            recorder=data.get('recorder', '')
        )


@dataclass
class CombatScore:
    """
    战斗评分数据模型

    Attributes:
        id: 评分记录ID(自增主键)
        log_id: 关联的战斗日志ID
        player_name: 玩家名称
        score_dps: DPS得分
        score_cc: 破控得分
        score_survival: 生存得分
        score_boon: 辅助得分
        total_score: 总分
        details: 详细评分数据(JSON字符串)
    """
    id: Optional[int] = None
    log_id: str = ''
    player_name: str = ''
    score_dps: float = 0.0
    score_cc: float = 0.0
    score_survival: float = 0.0
    score_boon: float = 0.0
    total_score: float = 0.0
    details: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'log_id': self.log_id,
            'player_name': self.player_name,
            'score_dps': self.score_dps,
            'score_cc': self.score_cc,
            'score_survival': self.score_survival,
            'score_boon': self.score_boon,
            'total_score': self.total_score,
            'details': self.details
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatScore':
        return cls(
            id=data.get('id'),
            log_id=data.get('log_id', ''),
            player_name=data.get('player_name', ''),
            score_dps=data.get('score_dps', 0.0),
            score_cc=data.get('score_cc', 0.0),
            score_survival=data.get('score_survival', 0.0),
            score_boon=data.get('score_boon', 0.0),
            total_score=data.get('total_score', 0.0),
            details=data.get('details', '')
        )


@dataclass
class FileFingerprint:
    """
    文件指纹数据模型

    用于检测重复上传和文件版本管理

    Attributes:
        id: 记录ID(自增主键)
        file_name: 文件名
        file_hash: 文件MD5哈希值
        upload_date: 上传日期
        log_id: 关联的战斗日志ID
        created_at: 创建时间
    """
    id: Optional[int] = None
    file_name: str = ''
    file_hash: str = ''
    upload_date: str = ''
    log_id: Optional[str] = None
    created_at: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_hash': self.file_hash,
            'upload_date': self.upload_date,
            'log_id': self.log_id,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileFingerprint':
        return cls(
            id=data.get('id'),
            file_name=data.get('file_name', ''),
            file_hash=data.get('file_hash', ''),
            upload_date=data.get('upload_date', ''),
            log_id=data.get('log_id'),
            created_at=data.get('created_at', '')
        )


@dataclass
class ParsedPlayerData:
    """
    解析后的玩家数据模型

    从日志文件中提取的原始玩家数据

    Attributes:
        name: 玩家名称
        account: 账户名
        profession: 职业
        dps: 秒伤
        cc: 破控伤害
        cleanses: 清洁次数
        strips: 剥离次数
        downs: 倒地次数
        deaths: 死亡次数
        buffs: BUFF覆盖率数据
    """
    name: str
    account: str = ''
    profession: str = ''
    dps: int = 0
    cc: int = 0
    cleanses: int = 0
    strips: int = 0
    downs: int = 0
    deaths: int = 0
    buffs: Dict[int, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'account': self.account,
            'profession': self.profession,
            'dps': self.dps,
            'cc': self.cc,
            'cleanses': self.cleanses,
            'strips': self.strips,
            'downs': self.downs,
            'deaths': self.deaths,
            'buffs': self.buffs
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedPlayerData':
        return cls(
            name=data.get('name', ''),
            account=data.get('account', ''),
            profession=data.get('profession', ''),
            dps=data.get('dps', 0),
            cc=data.get('cc', 0),
            cleanses=data.get('cleanses', 0),
            strips=data.get('strips', 0),
            downs=data.get('downs', 0),
            deaths=data.get('deaths', 0),
            buffs=data.get('buffs', {})
        )


@dataclass
class ParsedLogData:
    """
    解析后的战斗日志数据模型

    Attributes:
        log_id: 日志唯一标识
        encounter_name: 战斗名称
        duration: 战斗时长(秒)
        duration_ms: 战斗时长(毫秒)
        recorded_by: 记录者
        date: 战斗日期
        mode: 游戏模式
        players: 玩家数据列表
    """
    log_id: str
    encounter_name: str
    duration: float
    duration_ms: float
    recorded_by: str
    date: str
    mode: str
    players: List[ParsedPlayerData] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'log_id': self.log_id,
            'encounter_name': self.encounter_name,
            'duration': self.duration,
            'duration_ms': self.duration_ms,
            'recorded_by': self.recorded_by,
            'date': self.date,
            'mode': self.mode,
            'players': [p.to_dict() for p in self.players]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedLogData':
        players = [ParsedPlayerData.from_dict(p) for p in data.get('players', [])]
        return cls(
            log_id=data.get('log_id', ''),
            encounter_name=data.get('encounter_name', ''),
            duration=data.get('duration', 0.0),
            duration_ms=data.get('duration_ms', 0.0),
            recorded_by=data.get('recorded_by', ''),
            date=data.get('date', ''),
            mode=data.get('mode', ''),
            players=players
        )


@dataclass
class PlayerScore:
    """
    玩家评分数据模型

    Attributes:
        player_name: 玩家名称
        account: 账户名
        profession: 职业
        role: 角色定位
        scores: 各项得分
        total_score: 总分
        details: 详细信息
    """
    player_name: str
    account: str
    profession: str
    role: str
    scores: Dict[str, float]
    total_score: float
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'player_name': self.player_name,
            'account': self.account,
            'profession': self.profession,
            'role': self.role,
            'scores': self.scores,
            'total_score': self.total_score,
            'details': self.details
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerScore':
        return cls(
            player_name=data.get('player_name', ''),
            account=data.get('account', ''),
            profession=data.get('profession', ''),
            role=data.get('role', ''),
            scores=data.get('scores', {}),
            total_score=data.get('total_score', 0.0),
            details=data.get('details', {})
        )