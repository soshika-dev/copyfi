import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import { pinia } from '@/stores'
import '@/assets/main.css'

const app = createApp(App)

app.use(pinia)
app.use(router)

document.documentElement.lang = 'fa'
document.documentElement.dir = 'rtl'
document.documentElement.setAttribute('data-theme', 'silk')

app.mount('#app')
