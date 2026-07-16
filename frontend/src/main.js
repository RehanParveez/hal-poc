import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { useAuthStore } from '@/stores/auth.js'
import { i18n } from '@/i18n/index.js'

const app = createApp(App)
app.use(createPinia())
app.use(i18n) 
const auth = useAuthStore()
auth.restoreSession().then(() => {
app.use(router)
app.mount('#app')
})