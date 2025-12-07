import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'
import App from './App.vue'
import Search from './views/Search.vue'
import Downloads from './views/Downloads.vue'
import Settings from './views/Settings.vue'
import { API_BASE_URL } from './config.js'

// 配置 axios 默认 baseURL
axios.defaults.baseURL = API_BASE_URL

const routes = [
  { path: '/', component: Search },
  { path: '/downloads', component: Downloads },
  { path: '/settings', component: Settings }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
