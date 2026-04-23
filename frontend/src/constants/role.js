/**
 * 角色定位相关常量
 * 提供完整的职业角色分类体系，支持 GW2 所有职业和精英分支
 */

// 基础角色类型（主分类）
export const ROLE_TYPES = {
  DPS: 'DPS',
  SUPPORT: 'SUPPORT',
  CONDITION: 'CONDITION',
  HEALING: 'HEALING',
  CONTROL: 'CONTROL',
  UTILITY: 'UTILITY'
}

// 角色类型中文翻译
export const ROLE_TYPE_TRANSLATIONS = {
  'DPS': '输出',
  'SUPPORT': '辅助',
  'CONDITION': '症状',
  'HEALING': '治疗',
  'CONTROL': '控制',
  'UTILITY': '功能'
}

// 角色类型颜色样式
export const ROLE_TYPE_COLORS = {
  'DPS': {
    bg: 'bg-red-50',
    text: 'text-red-600',
    border: 'border-red-200'
  },
  'SUPPORT': {
    bg: 'bg-blue-50',
    text: 'text-blue-600',
    border: 'border-blue-200'
  },
  'CONDITION': {
    bg: 'bg-purple-50',
    text: 'text-purple-600',
    border: 'border-purple-200'
  },
  'HEALING': {
    bg: 'bg-green-50',
    text: 'text-green-600',
    border: 'border-green-200'
  },
  'CONTROL': {
    bg: 'bg-yellow-50',
    text: 'text-yellow-600',
    border: 'border-yellow-200'
  },
  'UTILITY': {
    bg: 'bg-gray-50',
    text: 'text-gray-600',
    border: 'border-gray-200'
  }
}

// 角色定位级别
export const ROLE_TIERS = {
  PRIMARY: 'PRIMARY',
  SECONDARY: 'SECONDARY',
  TERTIARY: 'TERTIARY'
}

export const ROLE_TIER_TRANSLATIONS = {
  'PRIMARY': '主要',
  'SECONDARY': '次要',
  'TERTIARY': '可选'
}

// 职业分支角色配置
// 结构：{ 职业名: { 分支名: { types: [主角色类型, 次要角色类型], description: 描述 } } }
export const PROFESSION_ROLES = {
  Guardian: {
    core: {
      types: ['SUPPORT', 'CONTROL'],
      description: '守护者核心以强大的团队保护能力著称，提供大量防御增益和控制技能。',
      icon: 'shield'
    },
    Dragonhunter: {
      types: ['DPS', 'CONTROL'],
      description: '猎龙者专注于对敌方目标的精准打击和陷阱控制。',
      icon: 'crossbow'
    },
    Firebrand: {
      types: ['SUPPORT', 'DPS'],
      description: '火战士提供灵活的辅助能力，既能治疗也能输出。',
      icon: 'book'
    },
    Willbender: {
      types: ['DPS', 'CONDITION'],
      description: '意志使是一个高机动性的输出职业，擅长快速接近和持续伤害。',
      icon: 'swiftness'
    }
  },

  Warrior: {
    core: {
      types: ['DPS', 'CONTROL'],
      description: '战士核心提供稳定的物理输出和基本的团队增益。',
      icon: 'sword'
    },
    Berserker: {
      types: ['DPS', 'CONDITION'],
      description: '狂战士专注于高爆发的近战输出和症状伤害。',
      icon: 'axe'
    },
    Spellbreaker: {
      types: ['DPS', 'CONTROL'],
      description: '破法者擅长打断敌方技能并提供反魔法支援。',
      icon: 'shield-break'
    },
    Bladesworn: {
      types: ['DPS', 'CONDITION'],
      description: '刃武者使用独特的龙之吐息进行毁灭性的范围攻击。',
      icon: 'dragon'
    }
  },

  Engineer: {
    core: {
      types: ['DPS', 'CONDITION'],
      description: '工程师核心具有多样化的技能组合，适应各种战斗情况。',
      icon: 'toolkit'
    },
    Scrapper: {
      types: ['SUPPORT', 'DPS'],
      description: '机械师提供强大的群体增益和防护能力。',
      icon: 'hammer'
    },
    Holosmith: {
      types: ['DPS', 'CONDITION'],
      description: '全息师在光与影之间切换，擅长高爆发伤害。',
      icon: 'photon'
    },
    Mechanist: {
      types: ['SUPPORT', 'DPS'],
      description: '机械师与机甲协同作战，提供远程辅助和输出。',
      icon: 'mech'
    }
  },

  Ranger: {
    core: {
      types: ['DPS', 'UTILITY'],
      description: '游侠核心与宠物配合，提供均衡的战斗能力。',
      icon: 'bow'
    },
    Druid: {
      types: ['HEALING', 'SUPPORT'],
      description: '德鲁伊是主要的治疗职业，擅长自然之力和范围治疗。',
      icon: 'nature'
    },
    Soulbeast: {
      types: ['DPS', 'CONDITION'],
      description: '魂兽师与野兽融合，提升自身输出和生存能力。',
      icon: 'beast'
    },
    Untamed: {
      types: ['DPS', 'CONTROL'],
      description: '不羁者释放宠物的野性，提供强大的控制能力。',
      icon: 'unleashed'
    }
  },

  Thief: {
    core: {
      types: ['DPS', 'CONDITION'],
      description: '潜行者核心擅长快速打击和症状施加。',
      icon: 'dagger'
    },
    Daredevil: {
      types: ['DPS', 'CONTROL'],
      description: '独行侠专注于高机动性的近战格斗和闪避。',
      icon: 'staff'
    },
    Deadeye: {
      types: ['DPS', 'CONDITION'],
      description: '神枪手使用狙击步枪提供远程精准打击。',
      icon: 'rifle'
    },
    Specter: {
      types: ['SUPPORT', 'DPS'],
      description: '幽影者穿梭于阴影之间，提供辅助和暗影伤害。',
      icon: 'shadow'
    }
  },

  Elementalist: {
    core: {
      types: ['DPS', 'CONDITION'],
      description: '元素使核心精通四系元素，提供多样化输出。',
      icon: 'element'
    },
    Tempest: {
      types: ['SUPPORT', 'DPS'],
      description: '暴风使擅长元素爆发，提供范围治疗和增益。',
      icon: 'storm'
    },
    Weaver: {
      types: ['DPS', 'CONDITION'],
      description: '编织者同时操控两种元素，实现极致的元素组合。',
      icon: 'dual'
    },
    Catalyst: {
      types: ['DPS', 'SUPPORT'],
      description: '催化剂以元素核心为中心，提供独特的球体辅助系统。',
      icon: 'orb'
    }
  },

  Mesmer: {
    core: {
      types: ['SUPPORT', 'CONDITION'],
      description: '幻术师核心擅长幻象和混乱，提供强大的控制能力。',
      icon: 'clone'
    },
    Chronomancer: {
      types: ['SUPPORT', 'CONTROL'],
      description: '时空术士操控时间，提供强大的群体增益和防护。',
      icon: 'clock'
    },
    Mirage: {
      types: ['DPS', 'CONDITION'],
      description: '幻灵师利用幻象和位移，擅长持续伤害和生存。',
      icon: 'prism'
    },
    Virtuoso: {
      types: ['DPS', 'CONDITION'],
      description: '艺术大师将幻术化为致命的飞刀，专注于输出。',
      icon: 'blades'
    }
  },

  Necromancer: {
    core: {
      types: ['CONDITION', 'DPS'],
      description: '死灵法师核心擅长症状伤害和生命值管理。',
      icon: 'death'
    },
    Reaper: {
      types: ['DPS', 'CONDITION'],
      description: '收割者挥舞巨大的镰刀，专注于近战症状输出。',
      icon: 'scythe'
    },
    Scourge: {
      types: ['SUPPORT', 'CONDITION'],
      description: '灾厄师提供强大的阴影辅助和范围控制。',
      icon: 'sand'
    },
    Harbinger: {
      types: ['DPS', 'CONDITION'],
      description: '先兆者将污秽转化为力量，擅长毒系伤害。',
      icon: 'elixir'
    }
  },

  Revenant: {
    core: {
      types: ['SUPPORT', 'DPS'],
      description: '魂武者核心借用传奇之力，提供多样化的支援。',
      icon: 'spirit'
    },
    Herald: {
      types: ['SUPPORT', 'DPS'],
      description: '先驱借用龙之力，提供强大的团队增益。',
      icon: 'dragon'
    },
    Renegade: {
      types: ['SUPPORT', 'CONDITION'],
      description: '背叛者借用传奇领主，提供范围辅助和症状输出。',
      icon: 'knight'
    },
    Vindicator: {
      types: ['DPS', 'SUPPORT'],
      description: '裁决者借用传奇战斗大师，实现攻守平衡。',
      icon: 'saint'
    }
  }
}

// 快速查询函数：获取职业分支的主要角色类型
export const getProfessionPrimaryRole = (profession, specialization) => {
  if (PROFESSION_ROLES[profession] && PROFESSION_ROLES[profession][specialization]) {
    const types = PROFESSION_ROLES[profession][specialization].types
    return types[0] || 'DPS'
  }
  return 'DPS'
}

// 快速查询函数：获取职业分支的所有角色类型
export const getProfessionRoles = (profession, specialization) => {
  if (PROFESSION_ROLES[profession] && PROFESSION_ROLES[profession][specialization]) {
    return PROFESSION_ROLES[profession][specialization].types
  }
  return ['DPS']
}

// 快速查询函数：获取职业分支的描述
export const getProfessionRoleDescription = (profession, specialization) => {
  if (PROFESSION_ROLES[profession] && PROFESSION_ROLES[profession][specialization]) {
    return PROFESSION_ROLES[profession][specialization].description
  }
  return ''
}

// 获取角色类型的默认样式类
export const getRoleTypeClasses = (roleType) => {
  const colors = ROLE_TYPE_COLORS[roleType] || ROLE_TYPE_COLORS['DPS']
  return `${colors.bg} ${colors.text}`
}

// 兼容旧版 API
export const ROLES = {
  DPS: 'DPS',
  SUPPORT: 'SUPPORT',
  UTILITY: 'UTILITY'
}

export const ROLE_BADGE_CLASSES = {
  'DPS': 'bg-red-50 text-red-600',
  'SUPPORT': 'bg-blue-50 text-blue-600',
  'UTILITY': 'bg-green-50 text-green-600',
  'CONDITION': 'bg-purple-50 text-purple-600',
  'HEALING': 'bg-green-50 text-green-600',
  'CONTROL': 'bg-yellow-50 text-yellow-600'
}

export const ROLE_TRANSLATIONS = {
  'DPS': '输出',
  'SUPPORT': '辅助',
  'UTILITY': '功能',
  'CONDITION': '症状',
  'HEALING': '治疗',
  'CONTROL': '控制'
}

// 根据旧版角色类型返回兼容的新类型
export const mapLegacyRole = (legacyRole) => {
  const mapping = {
    'DPS': 'DPS',
    'SUPPORT': 'SUPPORT',
    'UTILITY': 'UTILITY'
  }
  return mapping[legacyRole] || 'DPS'
}

// ========== 角色工具函数 ==========

export const translateRole = (role) => {
  return ROLE_TRANSLATIONS[role] || role || '输出'
}

export const getRoleBadgeClass = (role) => {
  return ROLE_BADGE_CLASSES[role] || 'bg-gray-50 text-gray-600'
}

export const getRoleColorClass = (role) => {
  const colors = ROLE_TYPE_COLORS[role] || ROLE_TYPE_COLORS['DPS']
  return `${colors.bg} ${colors.text}`
}

export const getRoleBorderClass = (role) => {
  const colors = ROLE_TYPE_COLORS[role] || ROLE_TYPE_COLORS['DPS']
  return colors.border || 'border-gray-200'
}

export const getProfessionAllRoles = (profession, specialization) => {
  return getProfessionRoles(profession, specialization)
}

export const getProfessionMainRole = (profession, specialization) => {
  return getProfessionPrimaryRole(profession, specialization)
}

export const getProfessionRoleInfo = (profession, specialization) => {
  const roles = getProfessionRoles(profession, specialization)
  const description = getProfessionRoleDescription(profession, specialization)
  const primaryRole = roles[0] || 'DPS'

  return {
    primaryRole,
    secondaryRole: roles[1] || null,
    allRoles: roles,
    description,
    colorClass: getRoleColorClass(primaryRole),
    badgeClass: getRoleBadgeClass(primaryRole)
  }
}

export const isHealerRole = (role) => {
  return role === ROLE_TYPES.HEALING || role === 'SUPPORT'
}

export const isDPSRole = (role) => {
  return role === ROLE_TYPES.DPS
}

export const isConditionRole = (role) => {
  return role === ROLE_TYPES.CONDITION
}

export const isSupportRole = (role) => {
  return role === ROLE_TYPES.SUPPORT
}

export const getAllSpecializations = (profession) => {
  if (PROFESSION_ROLES[profession]) {
    return Object.keys(PROFESSION_ROLES[profession])
  }
  return []
}

export const getAllProfessions = () => {
  return Object.keys(PROFESSION_ROLES)
}