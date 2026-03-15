import axios from 'axios'
import router from '@/router'
import { pinia } from '@/stores'
import { useAuthStore } from '@/stores/auth'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json'
  }
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('pastehub_access_token')
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})


http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const hasToken = Boolean(localStorage.getItem('pastehub_access_token'))
    const errorCode = error?.response?.data?.error?.code

    if (status === 401 && hasToken && !['paste_password_required', 'invalid_paste_password'].includes(errorCode)) {
      const authStore = useAuthStore(pinia)
      authStore.logout({ redirect: false, remote: false })
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }

    return Promise.reject(error)
  }
)

export default http
