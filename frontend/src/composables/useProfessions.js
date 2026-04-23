import { ref, computed } from 'vue'
import { getProfessions } from '../utils/api.js'

const professionsData = ref(null)
const isLoading = ref(false)
const error = ref(null)

// 从数组格式的职业数据中提取翻译
const translations = computed(() => {
  if (!professionsData.value || !Array.isArray(professionsData.value)) return {}
  
  const result = {}
  professionsData.value.forEach(item => {
    // 找到职业名称的键（第一个键）
    const professionKey = Object.keys(item).find(key => key !== 'colors' && key !== 'core' && key !== 'defaultRole' && !['SUPPORT', 'DPS', 'CONDITION', 'HEALING', 'CONTROL', 'UTILITY'].includes(key))
    if (professionKey) {
      result[professionKey] = item[professionKey]
    }
  })
  return result
})

// 从数组格式的职业数据中提取颜色
const colors = computed(() => {
  if (!professionsData.value || !Array.isArray(professionsData.value)) return {}
  
  const result = {}
  professionsData.value.forEach(item => {
    // 找到职业名称的键（第一个键）
    const professionKey = Object.keys(item).find(key => key !== 'colors' && key !== 'core' && key !== 'defaultRole' && !['SUPPORT', 'DPS', 'CONDITION', 'HEALING', 'CONTROL', 'UTILITY'].includes(key))
    if (professionKey && item.colors) {
      result[professionKey] = item.colors
    }
  })
  return result
})

// 角色类型配置
const roleTypes = computed(() => ({
  "DPS": {"name": "DPS", "color": {"bg": "bg-red-50", "text": "text-red-600", "border": "border-red-200"}},
  "SUPPORT": {"name": "SUPPORT", "color": {"bg": "bg-blue-50", "text": "text-blue-600", "border": "border-blue-200"}},
  "CONDITION": {"name": "CONDITION", "color": {"bg": "bg-purple-50", "text": "text-purple-600", "border": "border-purple-200"}},
  "HEALING": {"name": "HEALING", "color": {"bg": "bg-green-50", "text": "text-green-600", "border": "border-green-200"}},
  "CONTROL": {"name": "CONTROL", "color": {"bg": "bg-yellow-50", "text": "text-yellow-600", "border": "border-yellow-200"}},
  "UTILITY": {"name": "UTILITY", "color": {"bg": "bg-gray-50", "text": "text-gray-600", "border": "border-gray-200"}}
}))

// 角色类型翻译
const roleTypeTranslations = computed(() => ({
  "DPS": "输出",
  "SUPPORT": "辅助",
  "CONDITION": "症状",
  "HEALING": "治疗",
  "CONTROL": "控制",
  "UTILITY": "功能"
}))

// 从数组格式的职业数据中提取角色配置
const roleConfig = computed(() => {
  if (!professionsData.value || !Array.isArray(professionsData.value)) return {}
  
  const result = {}
  professionsData.value.forEach(item => {
    // 找到职业名称的键（第一个键）
    const professionKey = Object.keys(item).find(key => key !== 'colors' && key !== 'core' && key !== 'defaultRole' && !['SUPPORT', 'DPS', 'CONDITION', 'HEALING', 'CONTROL', 'UTILITY'].includes(key))
    if (professionKey && item.core) {
      // 确定职业类别（核心职业还是精英特长）
      const isCoreProfession = ['Guardian', 'Warrior', 'Engineer', 'Ranger', 'Thief', 'Elementalist', 'Mesmer', 'Necromancer', 'Revenant'].includes(professionKey)
      
      if (isCoreProfession) {
        // 核心职业
        if (!result[professionKey]) {
          result[professionKey] = {}
        }
        result[professionKey].core = item.core
      } else {
        // 精英特长，需要确定所属的核心职业
        let coreProfession = ''
        switch (professionKey) {
          case 'Firebrand':
          case 'Willbender':
          case 'Dragonhunter':
            coreProfession = 'Guardian'
            break
          case 'Berserker':
          case 'Spellbreaker':
          case 'Bladesworn':
            coreProfession = 'Warrior'
            break
          case 'Scrapper':
          case 'Holosmith':
          case 'Mechanist':
          case 'Kinetic':
            coreProfession = 'Engineer'
            break
          case 'Druid':
          case 'Soulbeast':
          case 'Untamed':
          case 'Sylvarin':
            coreProfession = 'Ranger'
            break
          case 'Daredevil':
          case 'Deadeye':
          case 'Specter':
          case 'Nightblade':
            coreProfession = 'Thief'
            break
          case 'Tempest':
          case 'Weaver':
          case 'Catalyst':
          case 'Animist':
            coreProfession = 'Elementalist'
            break
          case 'Chronomancer':
          case 'Mirage':
          case 'Virtuoso':
          case 'Bard':
            coreProfession = 'Mesmer'
            break
          case 'Reaper':
          case 'Scourge':
          case 'Harbinger':
          case 'Ritualist':
            coreProfession = 'Necromancer'
            break
          case 'Herald':
          case 'Renegade':
          case 'Vindicator':
          case 'ForbiddenOathkeeper':
            coreProfession = 'Revenant'
            break
        }
        
        if (coreProfession) {
          if (!result[coreProfession]) {
            result[coreProfession] = {}
          }
          result[coreProfession][professionKey] = item.core
        }
      }
    }
  })
  return result
})

// 从数组格式的职业数据中提取默认角色
const defaultRoles = computed(() => {
  if (!professionsData.value || !Array.isArray(professionsData.value)) return {}
  
  const result = {}
  professionsData.value.forEach(item => {
    // 找到职业名称的键（第一个键）
    const professionKey = Object.keys(item).find(key => key !== 'colors' && key !== 'core' && key !== 'defaultRole' && !['SUPPORT', 'DPS', 'CONDITION', 'HEALING', 'CONTROL', 'UTILITY'].includes(key))
    if (professionKey && item.defaultRole) {
      result[professionKey] = item.defaultRole
    }
  })
  return result
})

export function useProfessions() {
  const loadProfessions = async () => {
    if (professionsData.value) return professionsData.value
    if (isLoading.value) return null

    isLoading.value = true
    error.value = null

    try {
      const response = await getProfessions()
      if (response.data?.status === 'success') {
        professionsData.value = response.data.data
        return professionsData.value
      }
    } catch (e) {
      error.value = e.message
      console.error('Failed to load professions:', e)
    } finally {
      isLoading.value = false
    }
    return null
  }

  const translateProfession = (profession) => {
    if (!profession) return '未知'
    return translations.value[profession] || profession
  }

  const getProfessionColor = (profession) => {
    return colors.value[profession] || { bg: 'bg-gray-100', text: 'text-gray-600' }
  }

  const getProfessionClass = (profession) => {
    const color = getProfessionColor(profession)
    return `${color.bg} ${color.text}`
  }

  const getProfessionRoles = (profession, specialization) => {
    if (roleConfig.value[profession] && roleConfig.value[profession][specialization]) {
      return roleConfig.value[profession][specialization].types
    }
    return ['DPS']
  }

  const getProfessionPrimaryRole = (profession, specialization) => {
    const types = getProfessionRoles(profession, specialization)
    return types[0] || 'DPS'
  }

  const getProfessionRoleDescription = (profession, specialization) => {
    if (roleConfig.value[profession] && roleConfig.value[profession][specialization]) {
      return roleConfig.value[profession][specialization].description
    }
    return ''
  }

  const getRoleBadgeClass = (role) => {
    const roleType = roleTypes.value[role]
    if (roleType) {
      const color = roleType.color || {}
      return `${color.bg || 'bg-gray-50'} ${color.text || 'text-gray-600'}`
    }
    return 'bg-gray-50 text-gray-600'
  }

  const getRoleColorClass = (role) => {
    const roleType = roleTypes.value[role]
    if (roleType) {
      const color = roleType.color || {}
      return `${color.bg || 'bg-gray-50'} ${color.text || 'text-gray-600'}`
    }
    return 'bg-gray-50 text-gray-600'
  }

  const getRoleBorderClass = (role) => {
    const roleType = roleTypes.value[role]
    if (roleType) {
      const color = roleType.color || {}
      return color.border || 'border-gray-200'
    }
    return 'border-gray-200'
  }

  const translateRole = (role) => {
    return roleTypeTranslations.value[role] || role || '输出'
  }

  const isHealerRole = (role) => {
    return role === 'HEALING' || role === 'SUPPORT'
  }

  const isDPSRole = (role) => {
    return role === 'DPS'
  }

  const isConditionRole = (role) => {
    return role === 'CONDITION'
  }

  const isSupportRole = (role) => {
    return role === 'SUPPORT'
  }

  const getAllSpecializations = (profession) => {
    if (roleConfig.value[profession]) {
      return Object.keys(roleConfig.value[profession])
    }
    return []
  }

  const getAllProfessions = () => {
    return Object.keys(translations.value)
  }

  const getProfessionRoleInfo = (profession, specialization) => {
    if (roleConfig.value[profession] && roleConfig.value[profession][specialization]) {
      const config = roleConfig.value[profession][specialization]
      const primaryRole = config.types?.[0] || 'DPS'
      return {
        primaryRole,
        secondaryRole: config.types?.[1] || null,
        allRoles: config.types || [],
        description: config.description || '',
        colorClass: getRoleColorClass(primaryRole),
        badgeClass: getRoleBadgeClass(primaryRole)
      }
    }
    return null
  }

  const getDefaultRole = (profession) => {
    return defaultRoles.value[profession] || 'DPS'
  }

  const getProfessionType = (profession) => {
    // 首先从defaultRoles中获取默认角色
    const defaultRole = getDefaultRole(profession)
    if (defaultRole) return defaultRole
    
    // 如果defaultRoles中没有，则从roleConfig中获取
    for (const coreProfession in roleConfig.value) {
      if (roleConfig.value[coreProfession][profession]) {
        const types = roleConfig.value[coreProfession][profession].types
        if (types) {
          // types可能是对象或数组
          if (typeof types === 'object' && !Array.isArray(types)) {
            return Object.keys(types)[0] || 'DPS'
          } else if (Array.isArray(types)) {
            return types[0] || 'DPS'
          }
        }
      }
    }
    return 'DPS'
  }

  return {
    professionsData,
    isLoading,
    error,
    loadProfessions,
    translateProfession,
    getProfessionColor,
    getProfessionClass,
    getProfessionRoles,
    getProfessionPrimaryRole,
    getProfessionRoleDescription,
    getRoleBadgeClass,
    getRoleColorClass,
    getRoleBorderClass,
    translateRole,
    isHealerRole,
    isDPSRole,
    isConditionRole,
    isSupportRole,
    getAllSpecializations,
    getAllProfessions,
    getProfessionRoleInfo,
    getDefaultRole,
    getProfessionType,
    translations,
    colors,
    roleTypes,
    roleConfig,
    defaultRoles
  }
}