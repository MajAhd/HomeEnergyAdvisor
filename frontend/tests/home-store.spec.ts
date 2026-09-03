import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../src/api/client'
import { useHomeStore } from '../src/stores/home'
import type { AdviceResponse, Home, HomeCreate } from '../src/types/home'

vi.mock('../src/api/client', async () => {
  const actual = await vi.importActual<typeof import('../src/api/client')>('../src/api/client')
  return {
    ...actual,
    createHome: vi.fn(),
    generateAdvice: vi.fn(),
  }
})

import { createHome, generateAdvice } from '../src/api/client'

const PAYLOAD: HomeCreate = {
  size_sqm: 100,
  year_built: 1990,
  heating_type: 'gas',
  insulation_quality: 'poor',
  occupants: 3,
}

const HOME: Home = { id: 'home-1', ...PAYLOAD, created_at: '2026-01-01T00:00:00Z' }

const ADVICE: AdviceResponse = {
  home_id: 'home-1',
  summary: 'Summary',
  recommendations: [],
  generated_at: '2026-01-01T00:00:00Z',
  source: 'mock',
}

describe('useHomeStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(createHome).mockReset()
    vi.mocked(generateAdvice).mockReset()
  })

  it('creates the home then fetches advice, exposing both on success', async () => {
    vi.mocked(createHome).mockResolvedValue(HOME)
    vi.mocked(generateAdvice).mockResolvedValue(ADVICE)
    const store = useHomeStore()

    await store.submitHomeAndGetAdvice(PAYLOAD)

    expect(createHome).toHaveBeenCalledWith(PAYLOAD)
    expect(generateAdvice).toHaveBeenCalledWith('home-1')
    expect(store.home).toEqual(HOME)
    expect(store.advice).toEqual(ADVICE)
    expect(store.error).toBeNull()
    expect(store.isSubmittingHome).toBe(false)
    expect(store.isGeneratingAdvice).toBe(false)
  })

  it('sets a friendly error and skips the advice call when home creation fails', async () => {
    vi.mocked(createHome).mockRejectedValue(new ApiError('size_sqm must be positive', 422))
    const store = useHomeStore()

    await store.submitHomeAndGetAdvice(PAYLOAD)

    expect(generateAdvice).not.toHaveBeenCalled()
    expect(store.error).toBe('size_sqm must be positive')
    expect(store.advice).toBeNull()
  })

  it('surfaces a dedicated message when the LLM provider fails (502)', async () => {
    vi.mocked(createHome).mockResolvedValue(HOME)
    vi.mocked(generateAdvice).mockRejectedValue(new ApiError('provider unreachable', 502))
    const store = useHomeStore()

    await store.submitHomeAndGetAdvice(PAYLOAD)

    expect(store.home).toEqual(HOME)
    expect(store.error).toContain('AI advisor is unavailable')
    expect(store.advice).toBeNull()
  })

  it('reset clears home, advice, and error', async () => {
    vi.mocked(createHome).mockResolvedValue(HOME)
    vi.mocked(generateAdvice).mockResolvedValue(ADVICE)
    const store = useHomeStore()
    await store.submitHomeAndGetAdvice(PAYLOAD)

    store.reset()

    expect(store.home).toBeNull()
    expect(store.advice).toBeNull()
    expect(store.error).toBeNull()
  })
})
