import { defineStore } from 'pinia'
import { ApiError, createHome, generateAdvice } from '../api/client'
import type { AdviceResponse, Home, HomeCreate } from '../types/home'

interface HomeStoreState {
  home: Home | null
  advice: AdviceResponse | null
  isSubmittingHome: boolean
  isGeneratingAdvice: boolean
  error: string | null
}

export const useHomeStore = defineStore('home', {
  state: (): HomeStoreState => ({
    home: null,
    advice: null,
    isSubmittingHome: false,
    isGeneratingAdvice: false,
    error: null,
  }),

  actions: {
    /** Submit the form: create the home profile, then immediately request advice
     * for it. Two separate API calls (matching the two backend endpoints), but one
     * user action - the loading/error state below tracks whichever is in flight. */
    async submitHomeAndGetAdvice(payload: HomeCreate): Promise<void> {
      this.error = null
      this.advice = null
      this.isSubmittingHome = true
      try {
        this.home = await createHome(payload)
      } catch (err) {
        this.error = errorMessage(err)
        return
      } finally {
        this.isSubmittingHome = false
      }

      this.isGeneratingAdvice = true
      try {
        this.advice = await generateAdvice(this.home.id)
      } catch (err) {
        this.error = errorMessage(err)
      } finally {
        this.isGeneratingAdvice = false
      }
    },

    reset(): void {
      this.home = null
      this.advice = null
      this.error = null
    },
  },
})

function errorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 502) return `The AI advisor is unavailable right now: ${err.message}`
    if (err.status === 404) return 'That home profile could not be found.'
    return err.message
  }
  return 'Something unexpected went wrong.'
}
