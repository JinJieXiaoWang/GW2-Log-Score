import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/attendance',
    name: 'Attendance',
    component: () => import('../views/Attendance.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
