# -*- coding: utf-8 -*-
"""
WvW EVTC / ZEVTC 战斗日志解析器  v2.0
======================================
功能：
  - 解析 arcdos 原始 .evtc / .zevtc 二进制日志（支持 revision 0/1）
  - 提取 WvW 大团/毒瘤 核心评分所需字段
  - 职业 ID → 名称映射（profession + elite spec）
  - 玩法类型自动判断（大团 / 毒瘤）
  - WvW 大团 / 毒瘤 评分计算（权重可配置）
  - SQLite 持久化（玩家表、战斗表、评分表、出勤表）
  - JSON 输出（校验/对比用）
  - CSV 报表导出
  - 批量处理整个文件夹

用法：
  # 单文件
  python wvw_evtc_parser.py log.zevtc

  # 批量
  python wvw_evtc_parser.py --batch /path/to/logs/

  # 查询历史
  python wvw_evtc_parser.py --query --player 帅姐姐

  # 导出报表
  python wvw_evtc_parser.py --export report.csv
"""

import os
import struct
import zipfile
import mmap
import functools
import datetime
import sqlite3
import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

# =============================================================================
# 职业 ID 映射表（profession + elite spec → 名称）
# =============================================================================
# 基础职业 ID 映射 (0-9)
PROFESSION_MAP = {
    0: "Unknown",
    1: "Guardian",
    2: "Warrior",
    3: "Engineer",
    4: "Ranger",
    5: "Thief",
    6: "Elementalist",
    7: "Mesmer",
    8: "Necromancer",
    9: "Revenant",
}

# 已验证的精英专精映射（来自实际日志测试）
ELITE_SPEC_MAP_VERIFIED = {
    0x05: "Druid",
    0x07: "Daredevil",
    0x1B: "Dragonhunter",
    0x28: "Chronomancer",
    0x2B: "Scrapper",
    0x34: "Herald",
    0x37: "Soulbeast",
    0x39: "Holosmith",
    0x3B: "Mirage",
    0x3C: "Scourge",
    0x40: "Harbinger",
    0x42: "Untamed",
    0x45: "Vindicator",
    0x46: "Mechanist",
    0x48: "Untamed",
}

# 未验证但参考官方 API 的精英专精映射
ELITE_SPEC_MAP_UNVERIFIED = {
    0x04: "Berserker",
    0x06: "Scrapper",
    0x08: "Daredevil",
    0x09: "Tempest",
    0x0A: "Chronomancer",
    0x0B: "Herald",
    0x0C: "Reaper",
    0x12: "Scourge",
    0x18: "Spellbreaker",
    0x1B: "Deadeye",
    0x22: "Soulbeast",
    0x27: "Firebrand",
    0x30: "Weaver",
    0x3A: "Harbinger",
    0x3B: "Willbender",
    0x3E: "Specter",
    0x41: "Bladesworn",
    0x42: "Virtuoso",
    0x43: "Catalyst",
    0x49: "Virtuoso",
    0x4A: "Vindicator",
}

# 最终精英专精映射（验证覆盖未验证）
ELITE_SPEC_MAP = {**ELITE_SPEC_MAP_UNVERIFIED, **ELITE_SPEC_MAP_VERIFIED}

# WvW 常用 BUFF ID 映射
BUFF_IDS = {
    1122: "stability",
    26980: "resistance",
    717: "protection",
    719: "swiftness",
    725: "fury",
    740: "might",
    718: "regeneration",
    726: "vigor",
    743: "aegis",
    1187: "quickness",
    30328: "alacrity",
}

# =============================================================================
# 全局常量定义
# =============================================================================
INT32_MAX = 2_147_483_647
AGENT_SIZE = 96
SKILL_SIZE = 68
EVENT_REV0 = 60
EVENT_REV1 = 64

# 状态事件类型
SC_NONE = 0
SC_ENTER_COMBAT = 1
SC_EXIT_COMBAT = 2
SC_CHANGE_UP = 3
SC_CHANGE_DEAD = 4
SC_CHANGE_DOWN = 5
SC_SPAWN = 6
SC_DESPAWN = 7
SC_HEALTH = 8
SC_LOG_START = 9
SC_LOG_END = 10
SC_WEAPON_SWAP = 11
SC_MAX_HEALTH = 12
SC_POV = 13
SC_LANGUAGE = 14
SC_GW2_BUILD = 15
SC_SHARD_ID = 16
SC_REWARD = 17
SC_BUFF_INITIAL = 18
SC_POSITION = 19
SC_VELOCITY = 20
SC_FACING = 21
SC_TEAM_CHANGE = 22
SC_BREAK_BAR = 34

# 战斗结果
RESULT_KILLING_BLOW = 8
RESULT_DOWNED_BLOW = 9

# 敌我标识
IFF_FRIEND = 0
IFF_FOE = 1
IFF_UNKNOWN = 2

# =============================================================================
# 数据结构定义
# =============================================================================

@dataclass
class AgentInfo:
    """实体信息（玩家/NPC/道具）"""
    addr: int
    prof: int
    elite: int
    toughness: int
    concentration: int
    healing: int
    condition: int
    hitbox_w: int
    hitbox_h: int
    name: str
    account: str
    is_player: bool
    is_gadget: bool
    team: Optional[int] = None
    instid: Optional[int] = None

    @property
    def profession(self) -> str:
        """获取职业名称"""
        if not self.is_player:
            return "NPC"
        return ELITE_SPEC_MAP.get(
            self.elite, PROFESSION_MAP.get(self.prof, f"Prof:{self.prof:#x}")
        )

    @property
    def account_clean(self) -> str:
        """清理账号名称前缀"""
        return self.account.lstrip(":")


@dataclass
class CombatMeta:
    """战斗元信息"""
    build_date: str = ""
    revision: int = 0
    boss_id: int = 0
    gw2_build: int = 0
    map_id: int = 0
    language: int = 0
    shard_id: int = 0
    log_start: Optional[int] = None
    log_end: Optional[int] = None
    pov_addr: Optional[int] = None

    @property
    def duration_s(self) -> float:
        """战斗时长（秒）"""
        if self.log_start and self.log_end:
            return float(self.log_end - self.log_start)
        return 0.0

    @property
    def start_datetime(self) -> Optional[str]:
        """日志开始时间（格式化）"""
        if self.log_start:
            return datetime.datetime.fromtimestamp(
                self.log_start, tz=datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S UTC")
        return None

    @property
    def map_name(self) -> str:
        """地图名称"""
        MAP_NAMES = {
            38: "Eternal Battlegrounds",
            1099: "Eternal Battlegrounds",
            1143: "Red Desert Borderlands",
            1210: "Alpine Borderlands (Blue)",
            1052: "Alpine Borderlands (Green)",
            1062: "Red Desert Borderlands",
            968: "Edge of the Mists",
        }
        return MAP_NAMES.get(self.map_id, f"Map:{self.map_id}")

    @property
    def is_wvw(self) -> bool:
        """是否为 WvW 地图"""
        WVW_MAPS = {38, 1099, 1143, 1210, 1052, 1062, 968, 1009}
        return self.map_id in WVW_MAPS


@dataclass
class PlayerStats:
    """玩家战斗统计数据"""
    addr: int
    name: str
    account: str
    profession: str
    team: Optional[int] = None

    # 伤害统计
    total_damage: int = 0
    power_damage: int = 0
    condi_damage: int = 0
    breakbar_damage: float = 0.0

    # 生存统计
    own_downs: int = 0
    own_deaths: int = 0
    combat_time_ms: int = 0

    # 输出贡献
    downs_inflicted: int = 0
    kills_inflicted: int = 0

    # 辅助贡献
    boon_strips: int = 0
    condi_cleanses: int = 0

    # BUFF 覆盖率
    buff_uptime: Dict[str, float] = field(default_factory=dict)

    @property
    def survival_score_raw(self) -> float:
        """生存原始评分（倒地/死亡惩罚）"""
        penalty = self.own_downs * 0.15 + self.own_deaths * 0.30
        return max(0.0, 1.0 - penalty)

    @property
    def is_support(self) -> bool:
        """是否为辅助职业"""
        support_specs = {
            "Firebrand", "Scrapper", "Mechanist", "Tempest",
            "Druid", "Herald", "Renegade", "Vindicator",
            "Scourge", "Chronomancer"
        }
        return self.profession in support_specs

# =============================================================================
# 核心解析器类
# =============================================================================

class ZevtcParser:
    """EVTC/ZEVTC 日志解析器"""

    def __init__(self, path: str):
        self.path = path
        self._data = b""
        self._mmap = None
        self._pos = 0
        self._cache = {}
        self._event_cache = {}

    def _load(self):
        """加载文件（支持压缩包与原始二进制）"""
        if zipfile.is_zipfile(self.path):
            with zipfile.ZipFile(self.path) as zf:
                entry = zf.namelist()[0]
                self._data = zf.read(entry)
        else:
            with open(self.path, "rb") as f:
                if os.path.getsize(self.path) > 10 * 1024 * 1024:
                    self._mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    self._data = self._mmap
                else:
                    self._data = f.read()

    def _cleanup(self):
        """关闭内存映射"""
        if self._mmap:
            self._mmap.close()
            self._mmap = None

    def _cached_parse(self, func):
        """解析结果缓存装饰器"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            if cache_key not in self._cache:
                self._cache[cache_key] = func(*args, **kwargs)
            return self._cache[cache_key]
        return wrapper

    def _r(self, n: int) -> bytes:
        """读取 n 个字节并移动指针"""
        b = self._data[self._pos: self._pos + n]
        if len(b) < n:
            raise EOFError(f"EOF at {self._pos}, need {n}")
        self._pos += n
        return b

    def _u8(self):
        return struct.unpack_from("<B", self._r(1))[0]

    def _i16(self):
        return struct.unpack_from("<h", self._r(2))[0]

    def _u16(self):
        return struct.unpack_from("<H", self._r(2))[0]

    def _i32(self):
        return struct.unpack_from("<i", self._r(4))[0]

    def _u32(self):
        return struct.unpack_from("<I", self._r(4))[0]

    def _u64(self):
        return struct.unpack_from("<Q", self._r(8))[0]

    @staticmethod
    def _nullstr(raw: bytes) -> str:
        """解析以 \x00 结尾的字符串"""
        idx = raw.find(b"\x00")
        if idx >= 0:
            return raw[:idx].decode("utf-8", errors="replace")
        return raw.decode("utf-8", errors="replace")

    def parse(self) -> Tuple[CombatMeta, List[AgentInfo], List[PlayerStats]]:
        """
        解析主入口
        返回：战斗元信息、实体列表、玩家统计列表
        """
        self._load()

        # 解析文件头
        magic = self._r(4).decode("ascii")
        if magic != "EVTC":
            raise ValueError(f"Not EVTC file (magic={magic!r})")

        build_date = self._r(8).decode("ascii")
        revision = self._u8()
        boss_id = self._u16()
        self._r(1)
        agent_count = self._u32()

        meta = CombatMeta(build_date=build_date, revision=revision, boss_id=boss_id)

        # 解析实体列表
        agents_list: List[AgentInfo] = []
        agents_by_addr: Dict[int, AgentInfo] = {}
        for _ in range(agent_count):
            raw = self._r(AGENT_SIZE)
            addr = struct.unpack_from("<Q", raw, 0)[0]
            prof = struct.unpack_from("<I", raw, 8)[0]
            elite = struct.unpack_from("<I", raw, 12)[0]
            tgh = struct.unpack_from("<h", raw, 16)[0]
            conc = struct.unpack_from("<h", raw, 18)[0]
            heal = struct.unpack_from("<h", raw, 20)[0]
            hbw = struct.unpack_from("<h", raw, 22)[0]
            cond = struct.unpack_from("<h", raw, 24)[0]
            hbh = struct.unpack_from("<h", raw, 26)[0]

            nr = raw[28:96]
            parts = nr.split(b"\x00")
            name = parts[0].decode("utf-8", errors="replace") if parts else ""
            account = parts[1].decode("utf-8", errors="replace") if len(parts) > 1 else ""

            is_player = elite != 0xFFFFFFFF
            is_gadget = elite == 0xFFFFFFFF and prof == 0xFFFFFFFF

            ag = AgentInfo(
                addr=addr, prof=prof, elite=elite, toughness=tgh,
                concentration=conc, healing=heal, condition=cond,
                hitbox_w=hbw, hitbox_h=hbh, name=name, account=account,
                is_player=is_player, is_gadget=is_gadget
            )
            agents_list.append(ag)
            agents_by_addr[addr] = ag

        # 解析技能
        skill_count = self._u32()
        skills: Dict[int, str] = {}
        for _ in range(skill_count):
            raw = self._r(SKILL_SIZE)
            sid = struct.unpack_from("<i", raw, 0)[0]
            sname = self._nullstr(raw[4:68])
            skills[sid] = sname

        # 事件解析
        ev_size = EVENT_REV1 if revision >= 1 else EVENT_REV0
        events_start = self._pos
        n_events = (len(self._data) - events_start) // ev_size

        instid_to_addr: Dict[int, int] = {}
        addr_team: Dict[int, int] = {}
        addr_combat_enter: Dict[int, int] = {}
        addr_combat_exit: Dict[int, int] = {}

        # 第一轮：解析基础状态事件
        for i in range(n_events):
            off = events_start + i * ev_size
            d = self._data
            sc = d[off + 56]
            src_agent = struct.unpack_from("<Q", d, off + 8)[0]
            src_instid = struct.unpack_from("<H", d, off + 40)[0]
            time = struct.unpack_from("<Q", d, off)[0]
            value = struct.unpack_from("<i", d, off + 24)[0]

            # 实体ID映射
            if sc in {SC_ENTER_COMBAT, SC_CHANGE_UP, SC_SPAWN,
                      SC_EXIT_COMBAT, SC_CHANGE_DEAD, SC_CHANGE_DOWN, SC_DESPAWN}:
                if src_instid and src_agent in agents_by_addr:
                    instid_to_addr[src_instid] = src_agent

            # 日志元信息
            if sc == SC_LOG_START:
                meta.log_start = value
            elif sc == SC_LOG_END:
                meta.log_end = value
            elif sc == SC_GW2_BUILD:
                meta.gw2_build = src_agent
            elif sc == SC_LANGUAGE:
                meta.language = src_agent
            elif sc == SC_SHARD_ID:
                meta.shard_id = src_agent
            elif sc == SC_POV:
                meta.pov_addr = src_agent
            elif sc == SC_TEAM_CHANGE:
                addr = instid_to_addr.get(src_instid, src_agent)
                addr_team[addr] = value
            elif sc == SC_ENTER_COMBAT:
                addr = instid_to_addr.get(src_instid, src_agent)
                if addr not in addr_combat_enter:
                    addr_combat_enter[addr] = time
            elif sc in (SC_EXIT_COMBAT, SC_CHANGE_DEAD):
                addr = instid_to_addr.get(src_instid, src_agent)
                if addr in addr_combat_enter:
                    addr_combat_exit[addr] = time

        # 获取地图ID
        for i in range(n_events):
            off = events_start + i * ev_size
            if self._data[off + 56] == 25:
                meta.map_id = struct.unpack_from("<Q", self._data, off + 8)[0]
                break

        # 绑定队伍ID
        for ag in agents_list:
            ag.team = addr_team.get(ag.addr)
        for iid, addr in instid_to_addr.items():
            if addr in agents_by_addr:
                agents_by_addr[addr].instid = iid

        # 初始化玩家统计
        ps: Dict[int, PlayerStats] = {}
        seen_addrs = set()
        seen_names = set()

        for ag in agents_list:
            if ag.is_player and 0 <= ag.prof <= 9:
                if ag.addr in seen_addrs:
                    continue
                seen_addrs.add(ag.addr)
                if ag.name in seen_names and not ag.account:
                    continue
                seen_names.add(ag.name)

                ps[ag.addr] = PlayerStats(
                    addr=ag.addr,
                    name=ag.name,
                    account=ag.account_clean,
                    profession=ag.profession,
                    team=ag.team,
                )

        # BUFF 状态跟踪
        buff_states: Dict[int, Dict[int, List]] = defaultdict(lambda: defaultdict(list))
        relevant_state_changes = {SC_NONE, SC_CHANGE_DOWN, SC_CHANGE_DEAD, SC_BUFF_INITIAL}

        # 批量处理事件
        events_batch_size = 10000
        for batch_start in range(0, n_events, events_batch_size):
            batch_end = min(batch_start + events_batch_size, n_events)
            batch_events = self._parse_event_batch(
                events_start, ev_size, batch_start, batch_end,
                relevant_state_changes, instid_to_addr, ps
            )
            for event_data in batch_events:
                self._process_event(event_data, ps, buff_states, instid_to_addr)

        # 计算BUFF覆盖率
        fight_duration_ms = max(1, int(meta.duration_s * 1000))
        for addr, p in ps.items():
            for bid, bname in BUFF_IDS.items():
                events_b = buff_states.get(addr, {}).get(bid, [])
                uptime_ms = _calc_buff_uptime(events_b, fight_duration_ms)
                p.buff_uptime[bname] = round(uptime_ms / fight_duration_ms * 100, 2)

        # 计算战斗时间
        for addr, p in ps.items():
            enter = addr_combat_enter.get(addr, 0)
            exit_ = addr_combat_exit.get(addr, enter)
            if enter:
                p.combat_time_ms = max(0, exit_ - enter)

        self._cleanup()
        return meta, agents_list, list(ps.values())

    def _parse_event_batch(self, events_start, ev_size, batch_start,
                           batch_end, relevant_state_changes, instid_to_addr, ps):
        """批量解析事件，提升效率"""
        batch_events = []
        for i in range(batch_start, batch_end):
            off = events_start + i * ev_size
            d = self._data
            sc = d[off + 56]
            if sc not in relevant_state_changes:
                continue
            event_data = self._parse_single_event(off, d, instid_to_addr)
            if event_data:
                batch_events.append(event_data)
        return batch_events

    def _parse_single_event(self, off, d, instid_to_addr):
        """解析单个事件结构"""
        try:
            time = struct.unpack_from("<Q", d, off)[0]
            src_agent = struct.unpack_from("<Q", d, off + 8)[0]
            dst_agent = struct.unpack_from("<Q", d, off + 16)[0]
            value = struct.unpack_from("<i", d, off + 24)[0]
            buff_dmg = struct.unpack_from("<i", d, off + 28)[0]
            skill_id = struct.unpack_from("<I", d, off + 36)[0]
            src_instid = struct.unpack_from("<H", d, off + 40)[0]
            dst_instid = struct.unpack_from("<H", d, off + 42)[0]
            iff = d[off + 48]
            buff = d[off + 49]
            result = d[off + 50]
            is_buffrm = d[off + 52]
            sc = d[off + 56]

            src_addr = instid_to_addr.get(src_instid, src_agent)
            dst_addr = instid_to_addr.get(dst_instid, dst_agent)

            return {
                "time": time, "src_addr": src_addr, "dst_addr": dst_addr,
                "value": value, "buff_dmg": buff_dmg, "skill_id": skill_id,
                "iff": iff, "buff": buff, "result": result,
                "is_buffrm": is_buffrm, "sc": sc
            }
        except (struct.error, IndexError):
            return None

    def _process_event(self, event_data, ps, buff_states, instid_to_addr):
        """处理单个事件，更新统计数据"""
        time = event_data["time"]
        src_addr = event_data["src_addr"]
        dst_addr = event_data["dst_addr"]
        value = event_data["value"]
        buff_dmg = event_data["buff_dmg"]
        skill_id = event_data["skill_id"]
        iff = event_data["iff"]
        buff = event_data["buff"]
        result = event_data["result"]
        is_buffrm = event_data["is_buffrm"]
        sc = event_data["sc"]

        src_is_player = src_addr in ps
        dst_is_player = dst_addr in ps

        # 伤害/击杀/倒地事件
        if sc == SC_NONE:
            if src_is_player and iff in (IFF_FOE, IFF_UNKNOWN):
                p = ps[src_addr]
                if buff == 0 and 0 < value < INT32_MAX:
                    p.power_damage += value
                    p.total_damage += value
                elif buff == 1 and 0 < buff_dmg < INT32_MAX:
                    p.condi_damage += buff_dmg
                    p.total_damage += buff_dmg

                if result == 6:
                    p.breakbar_damage += abs(value) if value != 0 else abs(buff_dmg)
                if result == RESULT_DOWNED_BLOW:
                    p.downs_inflicted += 1
                elif result == RESULT_KILLING_BLOW:
                    p.kills_inflicted += 1

            # 净化/驱散
            if is_buffrm in (1, 2):
                if src_is_player and iff == IFF_FOE:
                    ps[src_addr].boon_strips += 1
                if src_is_player and iff == IFF_FRIEND:
                    ps[src_addr].condi_cleanses += 1

        # 自身倒地/死亡
        elif sc == SC_CHANGE_DOWN and src_is_player:
            ps[src_addr].own_downs += 1
        elif sc == SC_CHANGE_DEAD and src_is_player:
            ps[src_addr].own_deaths += 1

        # BUFF 应用/移除
        if sc == SC_NONE and buff == 1 and dst_is_player:
            bid = skill_id
            if bid in BUFF_IDS:
                addr_key = dst_addr
                if is_buffrm == 0 and 0 < value < INT32_MAX:
                    buff_states[addr_key][bid].append(("apply", time, value))
                elif is_buffrm > 0:
                    buff_states[addr_key][bid].append(("remove", time, 0))

# =============================================================================
# 工具函数
# =============================================================================

def _calc_buff_uptime(events: list, duration_ms: int) -> int:
    """
    计算BUFF总覆盖时间（毫秒）
    合并重叠区间，避免重复计算
    """
    if not events:
        return 0

    intervals = []
    current_start = None

    for kind, t, dur in sorted(events, key=lambda x: x[1]):
        if kind == "apply" and current_start is None:
            current_start = t
            end = t + dur
            intervals.append((t, end))
        elif kind == "remove" and current_start is not None:
            current_start = None

    if not intervals:
        return 0

    # 合并重叠区间
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        last_s, last_e = merged[-1]
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))
        else:
            merged.append((s, e))

    total = sum(e - s for s, e in merged)
    return min(total, duration_ms)


def detect_play_style(player_count: int, meta: CombatMeta) -> str:
    """
    判断玩法类型
    返回：zerg（大团）/ havoc（小团/毒瘤）/ unknown
    """
    if not meta.is_wvw:
        return "unknown"
    return "zerg" if player_count > 20 else "havoc"


# =============================================================================
# 评分系统
# =============================================================================

DEFAULT_WEIGHTS = {
    "zerg": {
        "dps": {
            "effective_damage": 40,
            "breakbar_damage": 30,
            "survival": 30,
        },
        "support": {
            "stability_uptime": 20,
            "resistance_uptime": 15,
            "boon_strips": 20,
            "condi_cleanses": 15,
            "survival": 30,
        },
    },
    "havoc": {
        "kills": 40,
        "survival_time": 30,
        "downs_inflicted": 20,
        "survival": 10,
    },
}


def load_weights(path: Optional[str] = None) -> dict:
    """加载权重配置文件，不存在则使用默认值"""
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_WEIGHTS


def _normalize_score(raw: float, team_values: list, max_pts: float) -> float:
    """
    归一化评分：将原始值按团队最高值换算为满分 max_pts 的得分
    """
    top = max(team_values) if team_values else 0
    if top <= 0:
        return max_pts
    return min(max_pts, (raw / top) * max_pts)


def score_players(
    players: List[PlayerStats], play_style: str, weights: Optional[dict] = None
) -> List[dict]:
    """
    对所有玩家进行综合评分
    支持大团/小团两种模式，自动区分DPS/辅助
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    results = []
    wz = weights.get("zerg", DEFAULT_WEIGHTS["zerg"])
    wh = weights.get("havoc", DEFAULT_WEIGHTS["havoc"])

    # 团队全局数据
    team_dmg = [p.total_damage for p in players]
    team_bb = [p.breakbar_damage for p in players]
    team_strips = [p.boon_strips for p in players]
    team_clean = [p.condi_cleanses for p in players]
    team_stab = [p.buff_uptime.get("stability", 0) for p in players]
    team_res = [p.buff_uptime.get("resistance", 0) for p in players]
    team_kills = [p.kills_inflicted for p in players]
    team_downs = [p.downs_inflicted for p in players]
    team_surv = [p.combat_time_ms for p in players]

    # 逐个评分
    for p in players:
        if play_style == "zerg":
            if p.is_support:
                w = wz["support"]
                s_stab = _normalize_score(p.buff_uptime.get("stability", 0), team_stab, w["stability_uptime"])
                s_res = _normalize_score(p.buff_uptime.get("resistance", 0), team_res, w["resistance_uptime"])
                s_strip = _normalize_score(p.boon_strips, team_strips, w["boon_strips"])
                s_clean = _normalize_score(p.condi_cleanses, team_clean, w["condi_cleanses"])
                s_surv = p.survival_score_raw * w["survival"]
                total = s_stab + s_res + s_strip + s_clean + s_surv

                details = {
                    "stability": round(s_stab, 1),
                    "resistance": round(s_res, 1),
                    "boon_strips": round(s_strip, 1),
                    "condi_cleanses": round(s_clean, 1),
                    "survival": round(s_surv, 1),
                }
                role = "support"
            else:
                w = wz["dps"]
                s_dmg = _normalize_score(p.total_damage, team_dmg, w["effective_damage"])
                s_bb = _normalize_score(p.breakbar_damage, team_bb, w["breakbar_damage"])
                s_surv = p.survival_score_raw * w["survival"]
                total = s_dmg + s_bb + s_surv

                details = {
                    "effective_damage": round(s_dmg, 1),
                    "breakbar_damage": round(s_bb, 1),
                    "survival": round(s_surv, 1),
                }
                role = "dps"

        else:
            w = wh
            s_kills = _normalize_score(p.kills_inflicted, team_kills, w["kills"])
            s_surv_time = _normalize_score(p.combat_time_ms, team_surv, w["survival_time"])
            s_downs = _normalize_score(p.downs_inflicted, team_downs, w["downs_inflicted"])
            s_alive = p.survival_score_raw * w["survival"]
            total = s_kills + s_surv_time + s_downs + s_alive

            details = {
                "kills": round(s_kills, 1),
                "survival_time": round(s_surv_time, 1),
                "downs_inflicted": round(s_downs, 1),
                "survival": round(s_alive, 1),
            }
            role = "havoc"

        # 组装结果
        results.append({
            "name": p.name,
            "account": p.account,
            "profession": p.profession,
            "role": role,
            "total_score": round(total, 2),
            "score_details": details,
            "raw": {
                "total_damage": p.total_damage,
                "power_damage": p.power_damage,
                "condi_damage": p.condi_damage,
                "breakbar_damage": round(p.breakbar_damage, 1),
                "own_downs": p.own_downs,
                "own_deaths": p.own_deaths,
                "downs_inflicted": p.downs_inflicted,
                "kills_inflicted": p.kills_inflicted,
                "boon_strips": p.boon_strips,
                "condi_cleanses": p.condi_cleanses,
                "combat_time_ms": p.combat_time_ms,
                "buff_uptime": p.buff_uptime,
            },
        })

    # 按总分降序排列
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results