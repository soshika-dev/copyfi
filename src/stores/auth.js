import { defineStore } from 'pinia'
import router from '@/router'
import { loginRequest, logoutRequest, registerRequest } from '@/services/api/auth'

function readUser() {
  const raw = localStorage.getItem('pastehub_user')
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('pastehub_access_token') || '',
    refreshToken: localStorage.getItem('pastehub_refresh_token') || '',
    user: readUser(),
    loading: false
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token)
  },
  actions: {
    setAuth(data) {
      this.token = data.access_token
      this.refreshToken = data.refresh_token
      this.user = data.user

      localStorage.setItem('pastehub_access_token', data.access_token)
      localStorage.setItem('pastehub_refresh_token', data.refresh_token)
      localStorage.setItem('pastehub_user', JSON.stringify(data.user))
    },
    clearAuth() {
      this.token = ''
      this.refreshToken = ''
      this.user = null
      localStorage.removeItem('pastehub_access_token')
      localStorage.removeItem('pastehub_refresh_token')
      localStorage.removeItem('pastehub_user')
    },
    async login(payload) {
      this.loading = true
      try {
        const data = await loginRequest({
          username: payload.identifier,
          password: payload.password
        })
        this.setAuth(data)
        return data
      } finally {
        this.loading = false
      }
    },
    async register(payload) {
      this.loading = true
      try {
        const data = await registerRequest(payload)
        this.setAuth(data)
        return data
      } finally {
        this.loading = false
      }
    },
    async fetchMe() {
      return this.user
    },
    async logout(options = { redirect: true, remote: true }) {
      if (options.remote) {
        await logoutRequest(this.refreshToken).catch(() => {})
      }
      this.clearAuth()
      if (options.redirect) {
        router.push('/login')
      }
    }
  }
})
