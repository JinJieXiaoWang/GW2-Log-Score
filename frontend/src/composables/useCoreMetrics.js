/**
 * 核心指标计算的组合式函数
 */

export function useCoreMetrics() {
  /**
   * 获取核心指标
   * @param {Object} details - 详情对象
   * @param {string} role - 角色定位
   * @returns {Array} 核心指标数组
   */
  const getCoreMetrics = (details, role) => {
    const metrics = []

    if (!details) return metrics

    if (role === 'DPS') {
      if (details.dps !== null && details.dps !== undefined) {
        metrics.push({ label: '伤害', value: details.dps, unit: '点/秒' })
      }
      if (details.cc !== null && details.cc !== undefined) {
        metrics.push({ label: '控制', value: details.cc, unit: '点' })
      }
      if (details.aps !== null && details.aps !== undefined) {
        metrics.push({ label: '秒攻', value: details.aps, unit: '次' })
      }
    } else if (role === 'SUPPORT') {
      if (details.damage_taken !== null && details.damage_taken !== undefined) {
        metrics.push({ label: '承伤', value: details.damage_taken, unit: '点' })
      }
      if (details.heal !== null && details.heal !== undefined) {
        metrics.push({ label: '治疗', value: details.heal, unit: '点' })
      }
      if (details.cc !== null && details.cc !== undefined) {
        metrics.push({ label: '控制', value: details.cc, unit: '点' })
      }
    } else if (role === 'UTILITY') {
      if (details.boon_strips !== null && details.boon_strips !== undefined) {
        metrics.push({ label: '剥瘤', value: details.boon_strips, unit: '次' })
      }
      if (details.cc !== null && details.cc !== undefined) {
        metrics.push({ label: '控制', value: details.cc, unit: '点' })
      }
      if (details.dps !== null && details.dps !== undefined) {
        metrics.push({ label: '伤害', value: details.dps, unit: '点/秒' })
      }
    }

    return metrics
  }

  return {
    getCoreMetrics
  }
}
