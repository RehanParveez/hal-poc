import { createRouter, createWebHistory } from 'vue-router'
import PlaceholderView from '../views/PlaceholderView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: PlaceholderView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router