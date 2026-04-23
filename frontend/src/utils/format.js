/**
 * 格式化相关工具函数
 */

/**
 * 格式化日期
 * @param {string} dateString - 日期字符串
 * @returns {string} 格式化后的日期
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

/**
 * 格式化数字（千分位）
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  if (typeof num !== 'number') return num
  return num.toLocaleString('zh-CN')
}

/**
 * 格式化指标值
 * @param {number} value - 指标值
 * @returns {string} 格式化后的值
 */
export const formatMetricValue = (value) => {
  if (value === null || value === undefined) return '0'
  if (typeof value === 'number') {
    if (value >= 1000) return value.toLocaleString('zh-CN')
    return value.toFixed(2)
  }
  return value
}

/**
 * 获取分数对应的颜色类
 * @param {number} score - 分数
 * @returns {string} Tailwind CSS 类名
 */
export const getScoreColorClass = (score) => {
  if (score >= 95) return 'text-indigo-600'
  if (score >= 90) return 'text-purple-600'
  if (score >= 85) return 'text-blue-600'
  if (score >= 80) return 'text-cyan-600'
  if (score >= 75) return 'text-teal-600'
  if (score >= 70) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  if (score >= 50) return 'text-orange-600'
  if (score >= 30) return 'text-red-600'
  return 'text-gray-400'
}

/**
 * 获取分数条对应的颜色类
 * @param {number} score - 分数
 * @returns {string} Tailwind CSS 类名
 */
export const getScoreBarColorClass = (score) => {
  if (score >= 90) return 'bg-indigo-600'
  if (score >= 80) return 'bg-blue-600'
  if (score >= 70) return 'bg-green-600'
  if (score >= 60) return 'bg-yellow-600'
  if (score >= 50) return 'bg-orange-600'
  return 'bg-red-600'
}
