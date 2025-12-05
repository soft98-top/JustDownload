import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Search from './views/Search.vue'
import Downloads from './views/Downloads.vue'
import Settings from './views/Settings.vue'

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
