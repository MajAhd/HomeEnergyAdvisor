import type { AdviceResponse, Home, HomeCreate } from '../types/home'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    throw new ApiError('Could not reach the server. Is the backend running?', 0)
  }

  if (!response.ok) {
    const detail = await extractErrorDetail(response)
    throw new ApiError(detail, response.status)
  }

  return (await response.json()) as T
}

async function extractErrorDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') return body.detail
    // FastAPI validation errors (422) return detail as a list of {msg, loc, ...}.
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((e) => (typeof e === 'object' && e && 'msg' in e ? String(e.msg) : String(e)))
        .join('; ')
    }
  } catch {
    // response body wasn't JSON - fall through to the generic message below.
  }
  return `Request failed with status ${response.status}`
}

export function createHome(payload: HomeCreate): Promise<Home> {
  return request<Home>('/api/homes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getHome(id: string): Promise<Home> {
  return request<Home>(`/api/homes/${id}`)
}

export function generateAdvice(homeId: string): Promise<AdviceResponse> {
  return request<AdviceResponse>(`/api/homes/${homeId}/advice`, { method: 'POST' })
}
