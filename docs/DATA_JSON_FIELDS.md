# Elite Insights data.json 字段说明文档

## 1. 基础信息 (根级别字段)

| 字段 | 类型 | 说明 |
|------|------|------|
| `eliteInsightsVersion` | `string` | Elite Insights 解析器版本号 |
| `triggerID` | `number` | 触发器ID |
| `eiEncounterID` | `number` | Elite Insights 战斗ID |
| `fightName` | `string` | 战斗名称 (WvW/PvP模式) |
| `encounterName` | `string` | 战斗名称 (PvE模式) |
| `fightIcon` | `string` | 战斗图标URL |
| `arcVersion` | `string` | ArcDPS 版本号 |
| `gW2Build` | `number` | GW2游戏内部版本号 |
| `language` | `string` | 日志语言 |
| `languageID` | `number` | 语言ID |
| `recordedBy` | `string` | 记录日志的玩家名称 |
| `recordedAccountBy` | `string` | 记录日志的玩家账号 |
| `timeStart` | `string` | 战斗开始时间 |
| `timeEnd` | `string` | 战斗结束时间 |
| `timeStartStd` | `string` | 标准化的战斗开始时间 |
| `timeEndStd` | `string` | 标准化的战斗结束时间 |
| `duration` | `string` | 战斗持续时间 (格式化字符串) |
| `durationMS` | `number` | 战斗持续时间 (毫秒) |
| `logStartOffset` | `number` | 日志开始偏移 |
| `success` | `boolean` | 战斗是否成功 |
| `isCM` | `boolean` | 是否是挑战模式 |
| `anonymous` | `boolean` | 是否是匿名模式 |
| `detailedWvW` | `boolean` | 是否是详细WvW日志 |
| `isWvW` | `boolean` | 是否是WvW模式 |
| `isPvP` | `boolean` | 是否是PvP模式 |
| `isRaid` | `boolean` | 是否是Raid副本 |
| `isStrike` | `boolean` | 是否是Strike副本 |
| `isFractal` | `boolean` | 是否是Fractal副本 |
| `fractalScale` | `number` | Fractal 难度规模 |

## 2. Targets (目标/敌人) 字段

`targets` 是一个数组，每个元素代表一个目标/敌人。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `number` | 目标ID |
| `name` | `string` | 目标名称 |
| `totalHealth` | `number` | 总血量 |
| `finalHealth` | `number` | 战斗结束时的血量 |
| `healthPercentBurned` | `number` | 受到伤害的百分比 |
| `condition` | `number` | 条件码 |
| `concentration` | `number` | 专注值 |
| `healing` | `number` | 治疗量 |
| `toughness` | `number` | 坚韧值 |
| `hitboxHeight` | `number` | 碰撞箱高度 |
| `hitboxWidth` | `number` | 碰撞箱宽度 |
| `instanceID` | `number` | 实例ID |
| `teamID` | `number` | 团队ID |
| `isFake` | `boolean` | 是否是假目标 |
| `firstAware` | `number` | 首次检测到的时间 |
| `lastAware` | `number` | 最后检测到的时间 |

### 2.1 Targets 子对象：dpsAll

| 字段 | 类型 | 说明 |
|------|------|------|
| `dps` | `number` | 秒伤 (每秒伤害) |
| `damage` | `number` | 总伤害 |
| `condiDps` | `number` | 条件伤害秒伤 |
| `condiDamage` | `number` | 条件总伤害 |
| `powerDps` | `number` | 直接伤害秒伤 |
| `powerDamage` | `number` | 直接总伤害 |
| `breakbarDamage` | `number` | 破盾伤害 |
| `actorDps` | `number` | 玩家秒伤 |
| `actorDamage` | `number` | 玩家总伤害 |
| `actorCondiDps` | `number` | 玩家条件伤害秒伤 |
| `actorCondiDamage` | `number` | 玩家条件总伤害 |
| `actorPowerDps` | `number` | 玩家直接伤害秒伤 |
| `actorPowerDamage` | `number` | 玩家直接总伤害 |
| `actorBreakbarDamage` | `number` | 玩家破盾伤害 |

### 2.2 Targets 子对象：statsAll

| 字段 | 类型 | 说明 |
|------|------|------|
| `totalDamageCount` | `number` | 总攻击次数 |
| `totalDmg` | `number` | 总伤害 |
| `directDamageCount` | `number` | 直接伤害次数 |
| `directDmg` | `number` | 直接总伤害 |
| `connectedDirectDamageCount` | `number` | 命中的直接伤害次数 |
| `connectedDirectDmg` | `number` | 命中的直接伤害量 |
| `connectedDamageCount` | `number` | 命中的伤害总次数 |
| `connectedDmg` | `number` | 命中的总伤害量 |
| `critableDirectDamageCount` | `number` | 可暴击的直接伤害次数 |
| `criticalRate` | `number` | 暴击率 |
| `criticalDmg` | `number` | 暴击伤害 |
| `flankingRate` | `number` | 侧击率 |
| `againstMovingRate` | `number` | 对移动目标攻击率 |
| `glanceRate` | `number` | 浅击率 |
| `missed` | `number` | 未命中次数 |
| `evaded` | `number` | 闪避次数 |
| `blocked` | `number` | 格挡次数 |
| `interrupts` | `number` | 打断次数 |
| `invulned` | `number` | 无敌次数 |
| `killed` | `number` | 击杀数 |
| `downed` | `number` | 击倒数 |
| `downContribution` | `number` | 击倒贡献值 |
| `connectedPowerCount` | `number` | 命中的直接伤害次数 |
| `connectedPowerAbove90HPCount` | `number` | 目标血量90%以上时的命中伤害次数 |
| `connectedConditionCount` | `number` | 命中的条件伤害次数 |
| `connectedConditionAbove90HPCount` | `number` | 目标血量90%以上时的命中条件伤害次数 |
| `againstDownedCount` | `number` | 对倒地目标的攻击次数 |
| `againstDownedDamage` | `number` | 对倒地目标的伤害 |

### 2.3 Targets 子对象：defenses

| 字段 | 类型 | 说明 |
|------|------|------|
| `damageTaken` | `number` | 受到的总伤害 |
| `downedDamageTaken` | `number` | 倒地时受到的伤害 |
| `breakbarDamageTaken` | `number` | 破盾时受到的伤害 |
| `blockedCount` | `number` | 格挡次数 |
| `evadedCount` | `number` | 闪避次数 |
| `missedCount` | `number` | 未命中次数 |
| `dodgeCount` | `number` | 闪避计数 |
| `invulnedCount` | `number` | 无敌计数 |
| `damageBarrier` | `number` | 护盾伤害 |
| `interruptedCount` | `number` | 被打断次数 |
| `downCount` | `number` | 倒地次数 |
| `downDuration` | `number` | 倒地持续时间 |
| `deadCount` | `number` | 死亡次数 |
| `deadDuration` | `number` | 死亡持续时间 |
| `dcCount` | `number` | 离线次数 |
| `dcDuration` | `number` | 离线持续时间 |
| `boonStrips` | `number` | 增益移除数 |
| `boonStripsTime` | `number` | 增益移除时间 |
| `conditionCleanses` | `number` | 条件清除数 |
| `conditionCleansesTime` | `number` | 条件清除时间 |

## 3. Players (玩家) 字段

`players` 是一个数组，每个元素代表一个玩家的数据。

### 3.1 Players 基础信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `account` | `string` | 玩家账号名，格式：`Name.XXXX` 或 `Name` |
| `group` | `number` | 团队分组 |
| `hasCommanderTag` | `boolean` | 是否有指挥官标记 |
| `profession` | `string` | 职业专精名称 |
| `friendlyNPC` | `boolean` | 是否是友好NPC |
| `notInSquad` | `boolean` | 是否不在小队中 |
| `guildID` | `string` | 公会ID |
| `weapons` | `string[]` | 武器配置数组 |

### 3.2 Players 子对象：dpsTargets、targetDamage1S、targetPowerDamage1S、targetConditionDamage1S

这些对象和Targets中的对应对象结构一致，代表对每个目标的伤害。

### 3.3 Players 子对象：targetDamageDist

伤害分布数据。

### 3.4 Players 子对象：dpsAll

结构同 Targets 的 `dpsAll`，代表对所有目标的综合伤害。

### 3.5 Players 子对象：statsTargets、statsAll

结构同 Targets 的对应对象。

### 3.6 Players 子对象：support

| 字段 | 类型 | 说明 |
|------|------|------|
| `resurrects` | `number` | 复活次数 |
| `resurrectTime` | `number` | 复活时间 |
| `condiCleanse` | `number` | 清除条件数 (队友) |
| `condiCleanseTime` | `number` | 清除条件时间 (队友) |
| `condiCleanseSelf` | `number` | 清除条件数 (自己) |
| `condiCleanseTimeSelf` | `number` | 清除条件时间 (自己) |
| `boonStrips` | `number` | 移除增益数 |
| `boonStripsTime` | `number` | 移除增益时间 |

### 3.7 Players 子对象：buffUptimes

增益覆盖数据，是一个数组，每个元素代表一个增益的信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `number` | 增益ID |
| `buffData` | `Object[]` | 增益数据 |
| `states` | `Array[]` | 增益状态 |
| `statesPerSource` | `Object` | 每个来源的增益状态 |

#### 3.7.1 buffData 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `uptime` | `number` | 覆盖百分比 |
| `presence` | `number` | 存在率 |
| `generated` | `Object` | 不同来源的生成量 |
| `overstacked` | `Object` | 超量堆叠量 |
| `wasted` | `Object` | 浪费量 |
| `unknownExtended` | `Object` | 未知来源的延长量 |
| `byExtension` | `Object` | 通过延长获得的量 |
| `extended` | `Object` | 延长给他人的量 |

## 4. 重要的增益ID (Common Buff IDs)

| ID | 名称 | 说明 |
|----|------|------|
| 717 | Regeneration | 再生 |
| 718 | Swiftness | 急速 |
| 725 | Fury | 狂怒 |
| 726 | Protection | 保护 |
| 740 | Quickness | 敏捷 |
| 1187 | Vigor | 活力 |
| 26980 | Stability | 稳固 |
| 26981 | Resistance | 抗性 |
| 9283 | Aegis | 圣盾 |
| etc. | - | - |

## 5. 文件中已有的玩家样例 (从 tests/data.json)

根据测试文件，data.json 包含的玩家：
- 夺魂者 (职业：Scourge)
- 机械师 (职业：Herald)
- 夺魂者 (职业：Renegade)
- 破法者 (职业：Spellbreaker)
- 独行侠 (职业：Soulbeast)
- 彩戏师 (职业：Bladesworn)
- 预告者 (职业：Mechanist)
- 裁决者 (职业：Willbender)
- 猎龙者 (职业：Dragonhunter)
- 流金师 (职业：Tempest)
- 等...

## 6. 数据解析注意事项

1. **account 字段解析**: 
   - 格式通常是 `PlayerName.XXXX` 或 `PlayerName`
   - 如果包含 '.'，可以提取 `.` 之前部分作为角色名，之后作为数字ID
   - 但也有像 "xxx" 这种没有数字ID的格式

2. **profession 字段**: 
   - 是专精名称，不是基础职业
   - 常见值：Scourge、Herald、Renegade、Spellbreaker、Soulbeast、Mechanist、Willbender、Tempest、Bladesworn、Dragonhunter 等

3. **日期和时间**:
   - 建议使用 `timeStartStd` 和 `timeEndStd` 字段，这些是标准化格式
   - 格式类似：`2026-04-19 22:11:55 +08:00`

4. **模式识别**:
   - 优先使用显式标记字段：`isWvW`、`isPvP`、`isRaid`、`isStrike`、`isFractal`、`detailedWvW`
   - 如无标记，可通过 `fightName` 或 `encounterName` 进行模糊匹配

5. **Non Squad Player**:
   - 当 `notInSquad` 为 `true` 或 `account` 缺失/异常时，可能是小队外的玩家
   - 此时应该做异常标记，便于用户识别
