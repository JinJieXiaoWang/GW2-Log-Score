/**
 * 应用配置常量
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
export const API_TIMEOUT = 10000

export const SCORE_RANGES = {
  EXCELLENT: 95,
  GREAT: 90,
  GOOD: 85,
  ABOVE_AVERAGE: 80,
  AVERAGE: 75,
  PASSING: 70,
  BELOW_AVERAGE: 60,
  POOR: 50,
  VERY_POOR: 30
}

export const SCORE_COLOR_CLASSES = {
  excellent: 'text-indigo-600',
  great: 'text-purple-600',
  good: 'text-blue-600',
  above_average: 'text-cyan-600',
  average: 'text-teal-600',
  passing: 'text-green-600',
  below_average: 'text-yellow-600',
  poor: 'text-orange-600',
  very_poor: 'text-red-600',
  default: 'text-gray-400'
}

export const SCORE_BAR_COLOR_CLASSES = {
  excellent: 'bg-indigo-600',
  great: 'bg-purple-600',
  good: 'bg-blue-600',
  above_average: 'bg-cyan-600',
  average: 'bg-teal-600',
  passing: 'bg-green-600',
  below_average: 'bg-yellow-600',
  poor: 'bg-orange-600',
  very_poor: 'bg-red-600'
}

export const MODES = {
  WVW: 'WvW',
  PVE: 'PvE',
  PVP: 'PvP'
}
