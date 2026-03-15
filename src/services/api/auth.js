import http from '@/services/http'

export async function loginRequest(payload) {
  const { data } = await http.post('/api/v1/auth/login', {
    username: payload.username,
    password: payload.password
  })
  return data.data
}

export async function registerRequest(payload) {
  const { data } = await http.post('/api/v1/auth/register', {
    username: payload.username,
    password: payload.password,
    email: payload.email || null
  })
  return data.data
}

export async function logoutRequest(refreshToken) {
  if (!refreshToken) return
  await http.post(
    '/api/v1/auth/logout',
    {},
    {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    }
  )
}
