/**
 * 玩家显示切换功能的组合式函数
 */
import { ref } from 'vue'

export function usePlayerDisplay() {
  const displayNameMode = ref({})

  /**
   * 获取玩家的唯一标识键
   * @param {Object} player - 玩家对象
   * @returns {string} 唯一键
   */
  const getPlayerKey = (player) => {
    return player.player_name || player.name || player.account || 'unknown'
  }

  /**
   * 获取当前的显示模式
   * @param {Object} player - 玩家对象
   * @returns {string} 'name' 或 'account'
   */
  const getPlayerDisplayNameMode = (player) => {
    const key = getPlayerKey(player)
    return displayNameMode.value[key] || 'name'
  }

  /**
   * 切换显示模式（角色名 <-> 账号ID）
   * @param {Object} player - 玩家对象
   */
  const toggleDisplayNameMode = (player) => {
    const key = getPlayerKey(player)
    const currentMode = getPlayerDisplayNameMode(player)
    displayNameMode.value[key] = currentMode === 'name' ? 'account' : 'name'
  }

  /**
   * 获取主要显示名称
   * @param {Object} player - 玩家对象
   * @returns {string} 显示的名称
   */
  const getDisplayName = (player) => {
    const name = player.player_name || player.name || ''
    const account = player.account || ''
    const mode = getPlayerDisplayNameMode(player)

    if (mode === 'name') {
      return name || account || 'Unknown'
    } else {
      return account || name || 'Unknown'
    }
  }

  /**
   * 获取次要显示名称
   * @param {Object} player - 玩家对象
   * @returns {string} 次要名称
   */
  const getSecondaryName = (player) => {
    const name = player.player_name || player.name || ''
    const account = player.account || ''
    const mode = getPlayerDisplayNameMode(player)

    if (mode === 'name' && account && account !== name) return account
    if (mode === 'account' && name && name !== account) return name

    return ''
  }

  /**
   * 判断是否需要显示次要名称
   * @param {Object} player - 玩家对象
   * @returns {boolean} 是否显示次要名称
   */
  const shouldShowSecondaryName = (player) => {
    const name = player.player_name || player.name || ''
    const account = player.account || ''
    return name && account && name !== account
  }

  /**
   * 获取显示名称的首字母
   * @param {Object} player - 玩家对象
   * @returns {string} 首字母
   */
  const getDisplayNameInitial = (player) => {
    const displayName = getDisplayName(player)
    return (displayName || 'U')[0]
  }

  return {
    displayNameMode,
    getPlayerKey,
    getPlayerDisplayNameMode,
    toggleDisplayNameMode,
    getDisplayName,
    getSecondaryName,
    shouldShowSecondaryName,
    getDisplayNameInitial
  }
}
