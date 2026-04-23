"""
WvW EVTC / ZEVTC 战斗日志解析器  v2.0
======================================
功能：
  - 解析 arcdps 原始 .evtc / .zevtc 二进制日志（支持 revision 0/1）
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

import struct, json, csv, sqlite3, zipfile, os, sys, argparse, datetime
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 职业 ID 映射表（profession + elite spec → 名称）
# ═══════════════════════════════════════════════════════════════

# prof (0-9) -> 基础职业名
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

# elite spec id -> 专精名（含 WvW 常见专精）
ELITE_SPEC_MAP = {
    # Guardian
    0x05: "Dragonhunter",
    0x27: "Firebrand",
    0x3b: "Willbender",
    # Warrior
    0x04: "Berserker",
    0x18: "Spellbreaker",
    0x41: "Bladesworn",
    # Engineer
    0x06: "Scrapper",
    0x2b: "Holosmith",
    0x46: "Mechanist",
    # Ranger
    0x07: "Druid",
    0x22: "Soulbeast",
    0x42: "Untamed",
    # Thief
    0x08: "Daredevil",
    0x1b: "Deadeye",
    0x3e: "Specter",
    # Elementalist
    0x09: "Tempest",
    0x30: "Weaver",
    0x41: "Catalyst",
    # Mesmer
    0x0a: "Chronomancer",
    0x28: "Mirage",
    0x49: "Virtuoso",
    # Necromancer
    0x0c: "Reaper",
    0x12: "Scourge",
    0x3a: "Harbinger",
    # Revenant
    0x0b: "Herald",
    0x39: "Renegade",
    0x4a: "Vindicator",
}

# WvW 常用 BUFF ID（来自 arcdps EVTC 规范 + GW2 API）
BUFF_IDS = {
    1122:  "stability",
    26980: "resistance",
    717:   "protection",
    719:   "swiftness",
    725:   "fury",
    740:   "might",
    718:   "regeneration",
    726:   "vigor",
    743:   "aegis",
    1187:  "quickness",
    30328: "alacrity",
}

# ═══════════════════════════════════════════════════════════════
# 常量
# ═══════════════════════════════════════════════════════════════

INT32_MAX      = 2_147_483_647
AGENT_SIZE     = 96
SKILL_SIZE     = 68
EVENT_REV0     = 60
EVENT_REV1     = 64

# statechange 枚举
SC_NONE         = 0
SC_ENTER_COMBAT = 1
SC_EXIT_COMBAT  = 2
SC_CHANGE_UP    = 3
SC_CHANGE_DEAD  = 4
SC_CHANGE_DOWN  = 5
SC_SPAWN        = 6
SC_DESPAWN      = 7
SC_HEALTH       = 8
SC_LOG_START    = 9
SC_LOG_END      = 10
SC_WEAPON_SWAP  = 11
SC_MAX_HEALTH   = 12
SC_POV          = 13
SC_LANGUAGE     = 14
SC_GW2_BUILD    = 15
SC_SHARD_ID     = 16
SC_REWARD       = 17
SC_BUFF_INITIAL = 18
SC_POSITION     = 19
SC_VELOCITY     = 20
SC_FACING       = 21
SC_TEAM_CHANGE  = 22
SC_BREAK_BAR    = 34

# result 枚举
RESULT_KILLING_BLOW = 8
RESULT_DOWNED_BLOW  = 9

# IFF
IFF_FRIEND  = 0
IFF_FOE     = 1
IFF_UNKNOWN = 2

# ═══════════════════════════════════════════════════════════════
# 数据结构
# ═══════════════════════════════════════════════════════════════

@dataclass
class AgentInfo:
    addr:          int
    prof:          int
    elite:         int
    toughness:     int
    concentration: int
    healing:       int
    condition:     int
    hitbox_w:      int
    hitbox_h:      int
    name:          str
    account:       str      # subgroup field (":account.1234")
    is_player:     bool
    is_gadget:     bool
    team:          Optional[int] = None
    instid:        Optional[int] = None

    @property
    def profession(self) -> str:
        if not self.is_player:
            return "NPC"
        return ELITE_SPEC_MAP.get(self.elite,
               PROFESSION_MAP.get(self.prof, f"Prof:{self.prof:#x}"))

    @property
    def account_clean(self) -> str:
        return self.account.lstrip(":")

@dataclass
class CombatMeta:
    """战斗基础信息"""
    build_date:    str  = ""
    revision:      int  = 0
    boss_id:       int  = 0
    gw2_build:     int  = 0
    map_id:        int  = 0
    language:      int  = 0
    shard_id:      int  = 0
    log_start:     Optional[int] = None   # unix timestamp
    log_end:       Optional[int] = None
    pov_addr:      Optional[int] = None

    @property
    def duration_s(self) -> float:
        if self.log_start and self.log_end:
            return float(self.log_end - self.log_start)
        return 0.0

    @property
    def start_datetime(self) -> Optional[str]:
        if self.log_start:
            return datetime.datetime.fromtimestamp(
                self.log_start, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        return None

    @property
    def map_name(self) -> str:
        MAP_NAMES = {
            1099: "Eternal Battlegrounds",
            1143: "Red Desert Borderlands",
            1210: "Alpine Borderlands (Blue)",
            1052: "Alpine Borderlands (Green)",
            1062: "Red Desert Borderlands",
            968:  "Edge of the Mists",
        }
        return MAP_NAMES.get(self.map_id, f"Map:{self.map_id}")

    @property
    def is_wvw(self) -> bool:
        WVW_MAPS = {1099, 1143, 1210, 1052, 1062, 968, 1009}
        return self.map_id in WVW_MAPS

@dataclass
class PlayerStats:
    """每位玩家的战斗统计数据"""
    addr:           int
    name:           str
    account:        str
    profession:     str
    team:           Optional[int] = None

    # 伤害
    total_damage:   int   = 0
    power_damage:   int   = 0
    condi_damage:   int   = 0
    breakbar_damage: float = 0.0

    # 自身存活
    own_downs:      int   = 0
    own_deaths:     int   = 0
    combat_time_ms: int   = 0   # 在战斗中的时间（ms）

    # 对敌效果
    downs_inflicted: int  = 0   # 击倒敌方
    kills_inflicted: int  = 0   # 击杀敌方（击败）

    # 辅助
    boon_strips:     int  = 0   # 撕BUFF
    condi_cleanses:  int  = 0   # 清除己方条件

    # BUFF 覆盖率（秒数，除以 duration 得到 %）
    buff_uptime:     Dict[str, float] = field(default_factory=dict)

    @property
    def survival_score_raw(self) -> float:
        """存活能力原始分（倒地/死亡越少越高，满分1.0）"""
        penalty = self.own_downs * 0.15 + self.own_deaths * 0.30
        return max(0.0, 1.0 - penalty)

    @property
    def is_support(self) -> bool:
        """根据职业判断是否为辅助（粗略判断）"""
        support_specs = {
            "Firebrand", "Scrapper", "Mechanist", "Tempest",
            "Druid", "Herald", "Renegade", "Vindicator",
            "Scourge", "Chronomancer",
        }
        return self.profession in support_specs


# ═══════════════════════════════════════════════════════════════
# 核心解析器
# ═══════════════════════════════════════════════════════════════

class ZevtcParser:
    def __init__(self, path: str):
        self.path    = path
        self._data   = b''
        self._pos    = 0

    # ── 文件加载 ─────────────────────────────────────────────

    def _load(self):
        if zipfile.is_zipfile(self.path):
            with zipfile.ZipFile(self.path) as zf:
                entry = zf.namelist()[0]
                self._data = zf.read(entry)
        else:
            with open(self.path, 'rb') as f:
                self._data = f.read()

    # ── 原始读取 ─────────────────────────────────────────────

    def _r(self, n: int) -> bytes:
        b = self._data[self._pos:self._pos + n]
        if len(b) < n:
            raise EOFError(f"EOF at {self._pos}, need {n}")
        self._pos += n
        return b

    def _u8(self):  return struct.unpack_from('<B', self._r(1))[0]
    def _i16(self): return struct.unpack_from('<h', self._r(2))[0]
    def _u16(self): return struct.unpack_from('<H', self._r(2))[0]
    def _i32(self): return struct.unpack_from('<i', self._r(4))[0]
    def _u32(self): return struct.unpack_from('<I', self._r(4))[0]
    def _u64(self): return struct.unpack_from('<Q', self._r(8))[0]

    @staticmethod
    def _nullstr(raw: bytes) -> str:
        idx = raw.find(b'\x00')
        return raw[:idx].decode('utf-8', errors='replace') if idx >= 0 else raw.decode('utf-8', errors='replace')

    # ── 解析入口 ─────────────────────────────────────────────

    def parse(self) -> Tuple[CombatMeta, List[AgentInfo], List[PlayerStats]]:
        self._load()

        # ── Header ──────────────────────────────────────────
        magic = self._r(4).decode('ascii')
        if magic != 'EVTC':
            raise ValueError(f"不是 EVTC 文件（magic={magic!r}）")
        build_date  = self._r(8).decode('ascii')
        revision    = self._u8()
        boss_id     = self._u16()
        self._r(1)                          # padding
        agent_count = self._u32()

        meta = CombatMeta(build_date=build_date, revision=revision, boss_id=boss_id)

        # ── Agents ──────────────────────────────────────────
        agents_list: List[AgentInfo] = []
        agents_by_addr: Dict[int, AgentInfo] = {}
        for _ in range(agent_count):
            raw  = self._r(AGENT_SIZE)
            addr = struct.unpack_from('<Q', raw, 0)[0]
            prof = struct.unpack_from('<I', raw, 8)[0]
            elite= struct.unpack_from('<I', raw, 12)[0]
            tgh  = struct.unpack_from('<h', raw, 16)[0]
            conc = struct.unpack_from('<h', raw, 18)[0]
            heal = struct.unpack_from('<h', raw, 20)[0]
            hbw  = struct.unpack_from('<h', raw, 22)[0]
            cond = struct.unpack_from('<h', raw, 24)[0]
            hbh  = struct.unpack_from('<h', raw, 26)[0]
            nr   = raw[28:96]
            parts = nr.split(b'\x00')
            name    = parts[0].decode('utf-8', errors='replace') if parts else ''
            account = parts[1].decode('utf-8', errors='replace') if len(parts) > 1 else ''
            is_player = (elite != 0xFFFFFFFF)
            is_gadget = (elite == 0xFFFFFFFF and prof == 0xFFFFFFFF)
            ag = AgentInfo(addr=addr, prof=prof, elite=elite,
                           toughness=tgh, concentration=conc, healing=heal,
                           condition=cond, hitbox_w=hbw, hitbox_h=hbh,
                           name=name, account=account,
                           is_player=is_player, is_gadget=is_gadget)
            agents_list.append(ag)
            agents_by_addr[addr] = ag

        # ── Skills ──────────────────────────────────────────
        skill_count = self._u32()
        skills: Dict[int, str] = {}
        for _ in range(skill_count):
            raw = self._r(SKILL_SIZE)
            sid  = struct.unpack_from('<i', raw, 0)[0]
            sname = self._nullstr(raw[4:68])
            skills[sid] = sname

        # ── Events（两遍扫描）──────────────────────────────
        ev_size = EVENT_REV1 if revision >= 1 else EVENT_REV0
        events_start = self._pos
        n_events = (len(self._data) - events_start) // ev_size

        # 遍历一：建立 instid→addr 映射 + 提取元数据 + 团队ID
        instid_to_addr: Dict[int, int] = {}
        addr_team:       Dict[int, int] = {}
        addr_combat_enter: Dict[int, int] = {}   # addr -> first enter_combat time
        addr_combat_exit:  Dict[int, int] = {}

        for i in range(n_events):
            off = events_start + i * ev_size
            d   = self._data
            sc  = d[off + 56]
            src_agent  = struct.unpack_from('<Q', d, off + 8)[0]
            src_instid = struct.unpack_from('<H', d, off + 40)[0]
            time       = struct.unpack_from('<Q', d, off)[0]
            value      = struct.unpack_from('<i', d, off + 24)[0]

            # instid 映射（从进战/复活/生成事件）
            if sc in (SC_ENTER_COMBAT, SC_CHANGE_UP, SC_SPAWN, SC_EXIT_COMBAT,
                       SC_CHANGE_DEAD, SC_CHANGE_DOWN, SC_DESPAWN):
                if src_instid and src_agent and src_agent in agents_by_addr:
                    instid_to_addr[src_instid] = src_agent

            # 元数据
            if sc == SC_LOG_START:   meta.log_start  = value
            elif sc == SC_LOG_END:   meta.log_end    = value
            elif sc == SC_GW2_BUILD: meta.gw2_build  = src_agent
            elif sc == SC_LANGUAGE:  meta.language   = src_agent
            elif sc == SC_SHARD_ID:  meta.shard_id   = src_agent
            elif sc == SC_POV:       meta.pov_addr   = src_agent
            elif sc == SC_TEAM_CHANGE:
                addr = instid_to_addr.get(src_instid, src_agent)
                addr_team[addr] = value

            # 战斗时间统计
            elif sc == SC_ENTER_COMBAT:
                addr = instid_to_addr.get(src_instid, src_agent)
                if addr not in addr_combat_enter:
                    addr_combat_enter[addr] = time
            elif sc in (SC_EXIT_COMBAT, SC_CHANGE_DEAD):
                addr = instid_to_addr.get(src_instid, src_agent)
                if addr in addr_combat_enter:
                    addr_combat_exit[addr] = time

        # ── 推断 map_id：从 statechange=25 ──────────────────
        for i in range(n_events):
            off = events_start + i * ev_size
            sc = self._data[off + 56]
            if sc == 25:  # MAP_ID
                meta.map_id = struct.unpack_from('<Q', self._data, off + 8)[0]
                break

        # 确定己方阵营
        pov_team = addr_team.get(meta.pov_addr) if meta.pov_addr else None
        player_addrs = {a.addr for a in agents_list if a.is_player}

        # 把 team 写回 agent
        for ag in agents_list:
            ag.team = addr_team.get(ag.addr)
        for iid, addr in instid_to_addr.items():
            if addr in agents_by_addr:
                agents_by_addr[addr].instid = iid

        # ── 遍历二：统计战斗数据 ────────────────────────────
        ps: Dict[int, PlayerStats] = {}
        for ag in agents_list:
            if ag.is_player:
                ps[ag.addr] = PlayerStats(
                    addr=ag.addr,
                    name=ag.name,
                    account=ag.account_clean,
                    profession=ag.profession,
                    team=ag.team,
                )

        # BUFF 时间积分：{addr: {buff_id: [on_ms, off_ms, ...]}}
        buff_states: Dict[int, Dict[int, List]] = defaultdict(lambda: defaultdict(list))

        for i in range(n_events):
            off = events_start + i * ev_size
            d   = self._data
            sc  = d[off + 56]

            time        = struct.unpack_from('<Q', d, off)[0]
            src_agent   = struct.unpack_from('<Q', d, off + 8)[0]
            dst_agent   = struct.unpack_from('<Q', d, off + 16)[0]
            value       = struct.unpack_from('<i', d, off + 24)[0]
            buff_dmg    = struct.unpack_from('<i', d, off + 28)[0]
            overstack   = struct.unpack_from('<I', d, off + 32)[0]
            skill_id    = struct.unpack_from('<I', d, off + 36)[0]
            src_instid  = struct.unpack_from('<H', d, off + 40)[0]
            dst_instid  = struct.unpack_from('<H', d, off + 42)[0]
            iff         = d[off + 48]
            buff        = d[off + 49]
            result      = d[off + 50]
            is_buffrm   = d[off + 52]
            is_ninety   = d[off + 53]
            is_fifty    = d[off + 54]

            src_addr = instid_to_addr.get(src_instid, src_agent)
            dst_addr = instid_to_addr.get(dst_instid, dst_agent)

            src_is_player = src_addr in ps
            dst_is_player = dst_addr in ps

            # ── 普通伤害事件（sc=0）──────────────────────────
            if sc == SC_NONE:
                if src_is_player and iff in (IFF_FOE, IFF_UNKNOWN):
                    p = ps[src_addr]
                    if buff == 0 and 0 < value < INT32_MAX:
                        p.power_damage += value
                        p.total_damage += value
                    elif buff == 1 and 0 < buff_dmg < INT32_MAX:
                        p.condi_damage += buff_dmg
                        p.total_damage += buff_dmg

                    # 破控伤害（breakbar_damage 在 overstack 字段，当 buff_dmg < 0 时）
                    # 实际上 breakbar 伤害在 buff=0 且 result 表示 breakbar hit
                    # arcdps 规范：breakbar_damage 在 value 字段当 buff=1 && is_activation=0
                    # 更可靠：result=6 (defiance bar hit)
                    if result == 6:  # CC / breakbar hit
                        p.breakbar_damage += abs(value) if value != 0 else abs(buff_dmg)

                    # 击倒 / 击杀敌方（通过 result 字段）
                    if result == RESULT_DOWNED_BLOW:
                        p.downs_inflicted += 1
                    elif result == RESULT_KILLING_BLOW:
                        p.kills_inflicted += 1

                # 撕 BUFF（buffremove=1/2，src=player，FOE 目标）
                if is_buffrm in (1, 2) and src_is_player and iff == IFF_FOE:
                    ps[src_addr].boon_strips += 1

                # 清除条件（buffremove=1/2，src=player，FRIEND 目标）
                if is_buffrm in (1, 2) and src_is_player and iff == IFF_FRIEND:
                    ps[src_addr].condi_cleanses += 1

            # ── 玩家倒地（sc=5，src=该玩家自身）────────────
            elif sc == SC_CHANGE_DOWN and src_is_player:
                ps[src_addr].own_downs += 1

            # ── 玩家死亡（sc=4）──────────────────────────────
            elif sc == SC_CHANGE_DEAD and src_is_player:
                ps[src_addr].own_deaths += 1

            # ── BUFF 状态跟踪（sc=18: buff_initial, sc=0 with buff=1）──
            # 用 statesPerSource 风格：记录 apply/remove 时间点
            # 简化：对 WvW 关键 buff，统计 buff 在玩家身上的总上行时间
            # 这里采用：buffremove=0 (applied) vs buffremove>0 (removed)
            if sc == SC_NONE and buff == 1 and dst_is_player:
                bid = skill_id
                if bid in BUFF_IDS:
                    addr_key = dst_addr
                    if is_buffrm == 0 and 0 < value < INT32_MAX:
                        # buff 应用：value = duration_ms
                        buff_states[addr_key][bid].append(('apply', time, value))
                    elif is_buffrm > 0:
                        buff_states[addr_key][bid].append(('remove', time, 0))

        # ── 计算 BUFF 覆盖率 ────────────────────────────────
        fight_duration_ms = max(1, int(meta.duration_s * 1000))
        for addr, p in ps.items():
            for bid, bname in BUFF_IDS.items():
                events_b = buff_states.get(addr, {}).get(bid, [])
                uptime_ms = _calc_buff_uptime(events_b, fight_duration_ms)
                p.buff_uptime[bname] = round(uptime_ms / fight_duration_ms * 100, 2)

        # ── 战斗时间 ────────────────────────────────────────
        for addr, p in ps.items():
            enter = addr_combat_enter.get(addr, 0)
            exit_ = addr_combat_exit.get(addr, enter)
            if enter:
                p.combat_time_ms = max(0, exit_ - enter)

        return meta, agents_list, list(ps.values())


def _calc_buff_uptime(events: list, duration_ms: int) -> int:
    """
    从 apply/remove 事件序列计算 buff 在 [0, duration_ms] 内的总覆盖时间（ms）

    Args:
        events: BUFF 事件列表，每个元素为 (kind, time, duration)
        duration_ms: 战斗总时长（毫秒）

    Returns:
        BUFF 覆盖总时间（毫秒）
    """
    if not events:
        return 0
    # 建立区间列表
    intervals = []
    current_start = None
    for kind, t, dur in sorted(events, key=lambda x: x[1]):
        if kind == 'apply' and current_start is None:
            current_start = t
            end = t + dur
            intervals.append((t, end))
        elif kind == 'remove' and current_start is not None:
            current_start = None
    # 合并重叠区间
    if not intervals:
        return 0
    intervals.sort()
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    # 截到战斗时间内
    total = sum(e - s for s, e in merged)
    return min(total, duration_ms)


# ═══════════════════════════════════════════════════════════════
# 玩法类型判断
# ═══════════════════════════════════════════════════════════════

def detect_play_style(player_count: int, meta: CombatMeta) -> str:
    """
    WvW 玩法类型：
      > 20 人  → zerg（大团）
      ≤ 20 人  → havoc（毒瘤/小队）
    """
    if not meta.is_wvw:
        return "unknown"
    return "zerg" if player_count > 20 else "havoc"


# ═══════════════════════════════════════════════════════════════
# 评分模块（权重可配置）
# ═══════════════════════════════════════════════════════════════

# 默认权重（可通过外部 JSON 覆盖）
DEFAULT_WEIGHTS = {
    "zerg": {
        "dps": {
            "effective_damage": 40,   # 总伤害（WvW 有效伤害，含 NPC）
            "breakbar_damage":  30,   # 破控
            "survival":         30,   # 存活（倒地/死亡惩罚）
        },
        "support": {
            "stability_uptime": 20,   # 稳固覆盖率
            "resistance_uptime": 15,  # 抗性覆盖率
            "boon_strips":      20,   # 撕 BUFF
            "condi_cleanses":   15,   # 清条件
            "survival":         30,   # 存活
        },
    },
    "havoc": {
        "kills":          40,
        "survival_time":  30,
        "downs_inflicted": 20,
        "survival":       10,
    }
}


def load_weights(path: Optional[str] = None) -> dict:
    if path and os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_WEIGHTS


def _normalize_score(raw: float, team_values: list, max_pts: float) -> float:
    """
    相对评分：以团队最高值为 100%，该玩家按比例得分。
    如果团队最高值为 0，所有人得 max_pts。
    """
    top = max(team_values) if team_values else 0
    if top <= 0:
        return max_pts
    return min(max_pts, (raw / top) * max_pts)


def score_players(players: List[PlayerStats], play_style: str,
                  weights: Optional[dict] = None) -> List[dict]:
    """计算每位玩家的评分，返回评分详情列表"""
    if weights is None:
        weights = DEFAULT_WEIGHTS
    results = []
    wz = weights.get("zerg", DEFAULT_WEIGHTS["zerg"])
    wh = weights.get("havoc", DEFAULT_WEIGHTS["havoc"])

    # 团队基准数据
    team_dmg    = [p.total_damage   for p in players]
    team_bb     = [p.breakbar_damage for p in players]
    team_strips = [p.boon_strips    for p in players]
    team_clean  = [p.condi_cleanses for p in players]
    team_stab   = [p.buff_uptime.get("stability", 0) for p in players]
    team_res    = [p.buff_uptime.get("resistance", 0) for p in players]
    team_kills  = [p.kills_inflicted for p in players]
    team_downs  = [p.downs_inflicted for p in players]
    team_surv   = [p.combat_time_ms  for p in players]

    for p in players:
        if play_style == "zerg":
            if p.is_support:
                w = wz.get("support", DEFAULT_WEIGHTS["zerg"]["support"])
                s_stab  = _normalize_score(p.buff_uptime.get("stability", 0),  team_stab,  w["stability_uptime"])
                s_res   = _normalize_score(p.buff_uptime.get("resistance", 0), team_res,   w["resistance_uptime"])
                s_strip = _normalize_score(p.boon_strips,   team_strips, w["boon_strips"])
                s_clean = _normalize_score(p.condi_cleanses, team_clean, w["condi_cleanses"])
                s_surv  = p.survival_score_raw * w["survival"]
                total   = s_stab + s_res + s_strip + s_clean + s_surv
                details = {"stability": round(s_stab, 1), "resistance": round(s_res, 1),
                           "boon_strips": round(s_strip, 1), "condi_cleanses": round(s_clean, 1),
                           "survival": round(s_surv, 1)}
                role = "support"
            else:
                w = wz.get("dps", DEFAULT_WEIGHTS["zerg"]["dps"])
                s_dmg  = _normalize_score(p.total_damage,    team_dmg, w["effective_damage"])
                s_bb   = _normalize_score(p.breakbar_damage, team_bb,  w["breakbar_damage"])
                s_surv = p.survival_score_raw * w["survival"]
                total  = s_dmg + s_bb + s_surv
                details = {"effective_damage": round(s_dmg, 1), "breakbar_damage": round(s_bb, 1),
                           "survival": round(s_surv, 1)}
                role = "dps"

        else:  # havoc
            w = wh
            s_kills = _normalize_score(p.kills_inflicted,  team_kills, w["kills"])
            s_surv  = _normalize_score(p.combat_time_ms,   team_surv,  w["survival_time"])
            s_downs = _normalize_score(p.downs_inflicted,  team_downs, w["downs_inflicted"])
            s_alive = p.survival_score_raw * w["survival"]
            total   = s_kills + s_surv + s_downs + s_alive
            details = {"kills": round(s_kills, 1), "survival_time": round(s_surv, 1),
                       "downs_inflicted": round(s_downs, 1), "survival": round(s_alive, 1)}
            role = "havoc"

        results.append({
            "name":        p.name,
            "account":     p.account,
            "profession":  p.profession,
            "role":        role,
            "total_score": round(total, 2),
            "score_details": details,
            "raw": {
                "total_damage":    p.total_damage,
                "power_damage":    p.power_damage,
                "condi_damage":    p.condi_damage,
                "breakbar_damage": round(p.breakbar_damage, 1),
                "own_downs":       p.own_downs,
                "own_deaths":      p.own_deaths,
                "downs_inflicted": p.downs_inflicted,
                "kills_inflicted": p.kills_inflicted,
                "boon_strips":     p.boon_strips,
                "condi_cleanses":  p.condi_cleanses,
                "combat_time_ms":  p.combat_time_ms,
                "buff_uptime":     p.buff_uptime,
            }
        })

    # 排序
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results


# ═══════════════════════════════════════════════════════════════
# SQLite 存储
# ═══════════════════════════════════════════════════════════════

DB_SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS players (
    account         TEXT PRIMARY KEY,
    name            TEXT,
    profession      TEXT,
    role            TEXT,
    last_seen       TEXT
);

CREATE TABLE IF NOT EXISTS combat_logs (
    log_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path       TEXT UNIQUE,
    file_hash       TEXT,
    fight_date      TEXT,
    fight_time      TEXT,
    duration_s      REAL,
    map_name        TEXT,
    map_id          INTEGER,
    play_style      TEXT,          -- zerg / havoc
    player_count    INTEGER,
    gw2_build       INTEGER,
    pov_account     TEXT,
    imported_at     TEXT
);

CREATE TABLE IF NOT EXISTS combat_scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id          INTEGER REFERENCES combat_logs(log_id),
    account         TEXT,
    name            TEXT,
    profession      TEXT,
    role            TEXT,
    total_score     REAL,
    score_json      TEXT,          -- JSON: score_details + raw
    total_damage    INTEGER,
    power_damage    INTEGER,
    condi_damage    INTEGER,
    breakbar_damage REAL,
    own_downs       INTEGER,
    own_deaths      INTEGER,
    downs_inflicted INTEGER,
    kills_inflicted INTEGER,
    boon_strips     INTEGER,
    condi_cleanses  INTEGER,
    combat_time_ms  INTEGER,
    buff_uptime_json TEXT           -- JSON: {buff_name: uptime%}
);

CREATE TABLE IF NOT EXISTS attendance (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    account     TEXT,
    log_id      INTEGER REFERENCES combat_logs(log_id),
    fight_date  TEXT,
    play_style  TEXT,
    attended    INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_scores_log    ON combat_scores(log_id);
CREATE INDEX IF NOT EXISTS idx_scores_acct   ON combat_scores(account);
CREATE INDEX IF NOT EXISTS idx_att_acct      ON attendance(account);
CREATE INDEX IF NOT EXISTS idx_att_date      ON attendance(fight_date);
CREATE INDEX IF NOT EXISTS idx_logs_date     ON combat_logs(fight_date);
"""


def get_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.executescript(DB_SCHEMA)
    conn.commit()
    return conn


def _file_hash(path: str) -> str:
    import hashlib
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def save_to_db(conn: sqlite3.Connection,
               meta: CombatMeta,
               agents: List[AgentInfo],
               players: List[PlayerStats],
               scores: List[dict],
               file_path: str,
               play_style: str):

    fhash = _file_hash(file_path)
    now   = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # 战斗时间
    if meta.log_start:
        dt_obj = datetime.datetime.fromtimestamp(meta.log_start, tz=datetime.timezone(datetime.timedelta(hours=8)))
        fight_date = dt_obj.strftime('%Y-%m-%d')
        fight_time = dt_obj.strftime('%H:%M:%S')
    else:
        fight_date = fight_time = ''

    # POV 账号
    pov_ag = next((a for a in agents if a.addr == meta.pov_addr), None)
    pov_account = pov_ag.account_clean if pov_ag else ''

    # 检查是否已导入
    row = conn.execute("SELECT log_id FROM combat_logs WHERE file_hash=?", (fhash,)).fetchone()
    if row:
        print(f"[SKIP] 已存在（hash 匹配）: {os.path.basename(file_path)}")
        return

    # 插入 combat_logs
    cur = conn.execute("""
        INSERT INTO combat_logs
        (file_path, file_hash, fight_date, fight_time, duration_s,
         map_name, map_id, play_style, player_count, gw2_build, pov_account, imported_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (file_path, fhash, fight_date, fight_time, meta.duration_s,
          meta.map_name, meta.map_id, play_style, len(players),
          meta.gw2_build, pov_account, now))
    log_id = cur.lastrowid

    # 插入 players（upsert）
    for p in players:
        conn.execute("""
            INSERT OR REPLACE INTO players (account, name, profession, role, last_seen)
            VALUES (?,?,?,?,?)
        """, (p.account, p.name, p.profession, '', fight_date))

    # 插入 combat_scores
    score_map = {s['account']: s for s in scores}
    for p in players:
        sc = score_map.get(p.account, {})
        conn.execute("""
            INSERT INTO combat_scores
            (log_id, account, name, profession, role, total_score,
             score_json, total_damage, power_damage, condi_damage,
             breakbar_damage, own_downs, own_deaths, downs_inflicted,
             kills_inflicted, boon_strips, condi_cleanses, combat_time_ms, buff_uptime_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (log_id, p.account, p.name, p.profession,
              sc.get('role', ''), sc.get('total_score', 0),
              json.dumps(sc, ensure_ascii=False),
              p.total_damage, p.power_damage, p.condi_damage,
              p.breakbar_damage, p.own_downs, p.own_deaths,
              p.downs_inflicted, p.kills_inflicted,
              p.boon_strips, p.condi_cleanses, p.combat_time_ms,
              json.dumps(p.buff_uptime, ensure_ascii=False)))

        # 出勤记录
        conn.execute("""
            INSERT INTO attendance (account, log_id, fight_date, play_style)
            VALUES (?,?,?,?)
        """, (p.account, log_id, fight_date, play_style))

    conn.commit()
    print(f"[DB]  已存储: {os.path.basename(file_path)}  log_id={log_id}  {play_style}  {fight_date}")


# ═══════════════════════════════════════════════════════════════
# JSON 输出（用于校验对比）
# ═══════════════════════════════════════════════════════════════

def save_to_json(path: str, meta: CombatMeta, agents: List[AgentInfo],
                 players: List[PlayerStats], scores: List[dict], play_style: str):
    doc = {
        "_meta": {
            "parser_version": "2.0",
            "source_file": os.path.basename(path.replace('.json', '')),
            "play_style": play_style,
            "is_wvw": meta.is_wvw,
        },
        "combat_info": {
            "build_date":    meta.build_date,
            "gw2_build":     meta.gw2_build,
            "map_id":        meta.map_id,
            "map_name":      meta.map_name,
            "duration_s":    meta.duration_s,
            "log_start":     meta.log_start,
            "start_time":    meta.start_datetime,
            "player_count":  len(players),
        },
        "players": [
            {
                "name":        p.name,
                "account":     p.account,
                "profession":  p.profession,
                "total_damage":    p.total_damage,
                "power_damage":    p.power_damage,
                "condi_damage":    p.condi_damage,
                "breakbar_damage": p.breakbar_damage,
                "own_downs":       p.own_downs,
                "own_deaths":      p.own_deaths,
                "downs_inflicted": p.downs_inflicted,
                "kills_inflicted": p.kills_inflicted,
                "boon_strips":     p.boon_strips,
                "condi_cleanses":  p.condi_cleanses,
                "combat_time_ms":  p.combat_time_ms,
                "buff_uptime_%":   p.buff_uptime,
            }
            for p in players
        ],
        "scores": scores,
        "npc_agents_count": sum(1 for a in agents if not a.is_player and not a.is_gadget),
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"[JSON] 已保存: {path}")


# ═══════════════════════════════════════════════════════════════
# CSV 报表导出
# ═══════════════════════════════════════════════════════════════

def export_csv(conn: sqlite3.Connection, out_path: str,
               start_date: str = '', end_date: str = '',
               player_filter: str = '', play_style_filter: str = ''):
    query = """
        SELECT
            cl.fight_date, cl.fight_time, cl.map_name, cl.play_style,
            cs.name, cs.account, cs.profession, cs.role,
            cs.total_score, cs.total_damage, cs.power_damage, cs.condi_damage,
            cs.breakbar_damage, cs.own_downs, cs.own_deaths,
            cs.downs_inflicted, cs.kills_inflicted,
            cs.boon_strips, cs.condi_cleanses, cs.combat_time_ms,
            cs.buff_uptime_json
        FROM combat_scores cs
        JOIN combat_logs cl ON cs.log_id = cl.log_id
        WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND cl.fight_date >= ?"; params.append(start_date)
    if end_date:
        query += " AND cl.fight_date <= ?"; params.append(end_date)
    if player_filter:
        query += " AND (cs.name LIKE ? OR cs.account LIKE ?)"; params += [f'%{player_filter}%']*2
    if play_style_filter:
        query += " AND cl.play_style = ?"; params.append(play_style_filter)
    query += " ORDER BY cl.fight_date DESC, cs.total_score DESC"

    rows = conn.execute(query, params).fetchall()
    headers = [
        "日期", "时间", "地图", "玩法", "角色名", "账号", "职业", "定位",
        "总分", "总伤害", "物理伤害", "条件伤害", "破控伤害",
        "倒地次数", "死亡次数", "击倒敌人", "击杀敌人",
        "撕BUFF", "清条件", "战斗时长(ms)", "稳固覆盖率%", "抗性覆盖率%"
    ]
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in rows:
            buff = json.loads(r[-1]) if r[-1] else {}
            row = list(r[:-1]) + [
                buff.get("stability", 0),
                buff.get("resistance", 0),
            ]
            w.writerow(row)
    print(f"[CSV] 已导出 {len(rows)} 条记录 → {out_path}")


# ═══════════════════════════════════════════════════════════════
# 历史查询
# ═══════════════════════════════════════════════════════════════

def query_history(conn: sqlite3.Connection, player: str = '', days: int = 30,
                  play_style: str = ''):
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    q = """
        SELECT cl.fight_date, cl.map_name, cl.play_style,
               cs.name, cs.profession, cs.role, cs.total_score,
               cs.total_damage, cs.own_downs, cs.own_deaths
        FROM combat_scores cs JOIN combat_logs cl ON cs.log_id=cl.log_id
        WHERE cl.fight_date >= ?
    """
    params = [cutoff]
    if player:
        q += " AND (cs.name LIKE ? OR cs.account LIKE ?)"
        params += [f'%{player}%', f'%{player}%']
    if play_style:
        q += " AND cl.play_style=?"
        params.append(play_style)
    q += " ORDER BY cl.fight_date DESC, cs.total_score DESC"
    rows = conn.execute(q, params).fetchall()
    print(f"\n{'日期':<12} {'地图':<24} {'玩法':<8} {'名称':<16} {'职业':<14} {'角色':<8} {'总分':>6} {'伤害':>10} {'倒':>4} {'死':>4}")
    print("─" * 110)
    for r in rows:
        print(f"{r[0]:<12} {r[1]:<24} {r[2]:<8} {r[3]:<16} {r[4]:<14} {r[5]:<8} {r[6]:>6.1f} {r[7]:>10,} {r[8]:>4} {r[9]:>4}")
    print(f"\n共 {len(rows)} 条记录")


# ═══════════════════════════════════════════════════════════════
# 出勤统计
# ═══════════════════════════════════════════════════════════════

def attendance_report(conn: sqlite3.Connection, period: str = 'month'):
    if period == 'week':
        days = 7
    elif period == 'month':
        days = 30
    else:
        days = 365
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    rows = conn.execute("""
        SELECT a.account, p.name, p.profession,
               COUNT(DISTINCT a.fight_date) as attend_days,
               COUNT(a.id) as attend_count,
               (SELECT COUNT(DISTINCT fight_date) FROM attendance
                WHERE fight_date >= ?) as total_days
        FROM attendance a
        LEFT JOIN players p ON a.account = p.account
        WHERE a.fight_date >= ?
        GROUP BY a.account
        ORDER BY attend_count DESC
    """, (cutoff, cutoff)).fetchall()
    total_days = rows[0][5] if rows else 1
    print(f"\n{'账号':<24} {'名称':<14} {'职业':<14} {'出勤天数':>8} {'出勤场次':>8} {'出勤率':>8}")
    print("─" * 80)
    for r in rows:
        rate = r[3] / total_days * 100 if total_days else 0
        print(f"{r[0]:<24} {r[1] or '':<14} {r[2] or '':<14} {r[3]:>8} {r[4]:>8} {rate:>7.1f}%")


# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════

def process_file(path: str, db_path: str, weights_path: Optional[str],
                 json_out: Optional[str] = None, verbose: bool = True):
    parser = ZevtcParser(path)
    try:
        meta, agents, players = parser.parse()
    except Exception as e:
        print(f"[ERR] 解析失败 {os.path.basename(path)}: {e}")
        return

    if not meta.is_wvw:
        print(f"[SKIP] 非WvW地图（map_id={meta.map_id}）: {os.path.basename(path)}")
        return

    play_style = detect_play_style(len(players), meta)
    weights    = load_weights(weights_path)
    scores     = score_players(players, play_style, weights)

    if verbose:
        print(f"\n{'═'*60}")
        print(f"  文件   : {os.path.basename(path)}")
        print(f"  时间   : {meta.start_datetime}")
        print(f"  地图   : {meta.map_name}")
        print(f"  时长   : {meta.duration_s:.0f}s")
        print(f"  玩法   : {play_style}  玩家数: {len(players)}")
        print(f"{'─'*60}")
        print(f"  {'名称':<16} {'职业':<14} {'角色':<8} {'总分':>6} {'总伤害':>10} {'倒地':>4} {'死亡':>4} {'破控':>8}")
        for s in scores:
            r = s['raw']
            print(f"  {s['name']:<16} {s['profession']:<14} {s['role']:<8} {s['total_score']:>6.1f}"
                  f" {r['total_damage']:>10,} {r['own_downs']:>4} {r['own_deaths']:>4} {r['breakbar_damage']:>8.0f}")
        print(f"{'═'*60}")

    # 存库
    conn = get_db(db_path)
    save_to_db(conn, meta, agents, players, scores, path, play_style)
    conn.close()

    # JSON 输出
    if json_out:
        save_to_json(json_out, meta, agents, players, scores, play_style)

    return meta, players, scores


def main():
    ap = argparse.ArgumentParser(description="WvW arcdps EVTC/ZEVTC 解析器 v2.0")
    ap.add_argument("input",       nargs="?",  help=".evtc/.zevtc 文件或文件夹（批量时用 --batch）")
    ap.add_argument("--batch",     action="store_true", help="批量解析文件夹内所有 .evtc/.zevtc")
    ap.add_argument("--db",        default="wvw_logs.db", help="SQLite 数据库路径")
    ap.add_argument("--json",      help="输出 JSON 路径（校验用）")
    ap.add_argument("--weights",   help="评分权重 JSON 配置路径")
    ap.add_argument("--export",    help="导出 CSV 报表路径")
    ap.add_argument("--query",     action="store_true", help="查询历史记录")
    ap.add_argument("--attendance",action="store_true", help="出勤统计报告")
    ap.add_argument("--player",    help="过滤玩家名称/账号")
    ap.add_argument("--days",      type=int, default=30, help="查询最近N天")
    ap.add_argument("--style",     choices=["zerg","havoc"], help="玩法类型过滤")
    ap.add_argument("--period",    default="month", choices=["week","month","year"])
    args = ap.parse_args()

    # 查询/报表模式（不需要 input）
    if args.query or args.attendance or args.export:
        conn = get_db(args.db)
        if args.query:
            query_history(conn, player=args.player or '', days=args.days,
                          play_style=args.style or '')
        if args.attendance:
            attendance_report(conn, period=args.period)
        if args.export:
            export_csv(conn, args.export, player_filter=args.player or '',
                       play_style_filter=args.style or '')
        conn.close()
        return

    if not args.input:
        ap.print_help()
        return

    # 批量模式
    if args.batch or os.path.isdir(args.input):
        folder = Path(args.input)
        files  = list(folder.glob("**/*.zevtc")) + list(folder.glob("**/*.evtc"))
        print(f"[批量] 找到 {len(files)} 个日志文件")
        for f in sorted(files):
            json_out = str(f) + ".json" if args.json else None
            process_file(str(f), args.db, args.weights, json_out)
        print(f"\n[完成] 共处理 {len(files)} 个文件")
        return

    # 单文件模式
    json_out = args.json
    if json_out is None and args.input:
        base = args.input.rsplit('.', 1)[0]
        json_out = base + "_parsed.json"

    process_file(args.input, args.db, args.weights, json_out, verbose=True)


if __name__ == "__main__":
    main()
