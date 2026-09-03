import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError, createHome, generateAdvice, getHome } from '../src/api/client'
import type { HomeCreate } from '../src/types/home'

const VALID_PAYLOAD: HomeCreate = {
  size_sqm: 100,
  year_built: 1990,
  heating_type: 'gas',
  insulation_quality: 'poor',
  occupants: 3,
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('api client', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('createHome posts the payload and returns the parsed home', async () => {
    const home = { id: 'abc', ...VALID_PAYLOAD, created_at: '2026-01-01T00:00:00Z' }
    vi.mocked(fetch).mockResolvedValue(jsonResponse(home, 201))

    const result = await createHome(VALID_PAYLOAD)

    expect(result).toEqual(home)
    const [url, init] = vi.mocked(fetch).mock.calls[0]!
    expect(String(url)).toContain('/api/homes')
    expect(init?.method).toBe('POST')
    expect(JSON.parse(init?.body as string)).toEqual(VALID_PAYLOAD)
  })

  it('getHome requests the home by id', async () => {
    const home = { id: 'abc', ...VALID_PAYLOAD, created_at: '2026-01-01T00:00:00Z' }
    vi.mocked(fetch).mockResolvedValue(jsonResponse(home))

    await getHome('abc')

    const [url] = vi.mocked(fetch).mock.calls[0]!
    expect(String(url)).toContain('/api/homes/abc')
  })

  it('generateAdvice posts to the advice endpoint', async () => {
    const advice = {
      home_id: 'abc',
      summary: 'ok',
      recommendations: [],
      generated_at: '2026-01-01T00:00:00Z',
      source: 'mock',
    }
    vi.mocked(fetch).mockResolvedValue(jsonResponse(advice))

    await generateAdvice('abc')

    const [url, init] = vi.mocked(fetch).mock.calls[0]!
    expect(String(url)).toContain('/api/homes/abc/advice')
    expect(init?.method).toBe('POST')
  })

  it('throws ApiError with the backend detail message on a 4xx/5xx response', async () => {
    vi.mocked(fetch).mockResolvedValue(jsonResponse({ detail: 'Home not found' }, 404))

    await expect(getHome('missing')).rejects.toMatchObject(new ApiError('Home not found', 404))
  })

  it('joins FastAPI validation error lists into one message', async () => {
    vi.mocked(fetch).mockResolvedValue(
      jsonResponse({ detail: [{ msg: 'field required', loc: ['body', 'size_sqm'] }] }, 422),
    )

    await expect(createHome(VALID_PAYLOAD)).rejects.toThrow('field required')
  })

  it('throws a network ApiError when fetch itself fails', async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError('network down'))

    await expect(getHome('abc')).rejects.toMatchObject({ status: 0 })
  })
})
