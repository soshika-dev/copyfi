import http from '@/services/http'

function mapCreatePayload(payload) {
  return {
    title: payload.title || null,
    content: payload.content,
    language: payload.language || null,
    visibility: payload.visibility,
    password: payload.password || null,
    expires_in: payload.expire_at || 'never',
    burn_after_read: false,
    tags: []
  }
}

export async function createPasteRequest(payload) {
  const { data } = await http.post('/api/v1/pastes', mapCreatePayload(payload))
  return data.data
}

export async function createFilePasteRequest(payload) {
  const formData = new FormData()
  formData.append('file', payload.file)
  formData.append('visibility', payload.visibility || 'unlisted')
  formData.append('expires_in', payload.expire_at || 'never')
  formData.append('burn_after_read', 'false')

  if (payload.title?.trim()) {
    formData.append('title', payload.title.trim())
  }
  if (payload.password?.trim()) {
    formData.append('password', payload.password.trim())
  }

  const { data } = await http.post('/api/v1/pastes/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return data.data
}

export async function getPasteByIdRequest(slug, password = null) {
  const headers = {}
  if (password) {
    headers['X-Paste-Password'] = password
  }

  const { data } = await http.get(`/api/v1/pastes/${slug}`, {
    headers
  })
  return data.data
}

export async function getPasteRawRequest(slug, password = null) {
  const headers = {}
  if (password) {
    headers['X-Paste-Password'] = password
  }

  const { data } = await http.get(`/api/v1/pastes/${slug}/raw`, {
    headers,
    responseType: 'text'
  })
  return data
}

export async function downloadPasteFileRequest(slug, password = null) {
  const headers = {}
  if (password) {
    headers['X-Paste-Password'] = password
  }

  const response = await http.get(`/api/v1/pastes/${slug}/download`, {
    headers,
    responseType: 'blob'
  })
  return response.data
}

export async function reportPasteRequest(slug, reason) {
  const { data } = await http.post(`/api/v1/pastes/${slug}/report`, { reason })
  return data.data
}

export async function getRecentPastesRequest(page = 1, limit = 10) {
  const { data } = await http.get('/api/v1/pastes/recent', {
    params: { page, limit }
  })
  return data
}

export async function getMyPastesRequest(page = 1, limit = 20) {
  const { data } = await http.get('/api/v1/me/pastes', {
    params: { page, limit }
  })
  return data
}
