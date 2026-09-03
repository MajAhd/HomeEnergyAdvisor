import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import AdviceList from '../src/components/AdviceList.vue'
import RecommendationCard from '../src/components/RecommendationCard.vue'
import type { AdviceResponse } from '../src/types/home'

const ADVICE: AdviceResponse = {
  home_id: 'home-1',
  summary: 'A drafty home with room for improvement.',
  recommendations: [
    {
      title: 'Low priority item',
      description: 'desc',
      priority: 'low',
      category: 'behavioral',
      estimated_annual_savings_eur: 50,
    },
    {
      title: 'High priority item',
      description: 'desc',
      priority: 'high',
      category: 'insulation',
      estimated_annual_savings_eur: null,
    },
    {
      title: 'Medium priority item',
      description: 'desc',
      priority: 'medium',
      category: 'heating',
      estimated_annual_savings_eur: 200,
    },
  ],
  generated_at: '2026-01-01T00:00:00Z',
  source: 'llm',
}

describe('AdviceList', () => {
  it('renders the summary and every recommendation', () => {
    const wrapper = mount(AdviceList, { props: { advice: ADVICE } })

    expect(wrapper.text()).toContain(ADVICE.summary)
    expect(wrapper.findAllComponents(RecommendationCard)).toHaveLength(3)
    expect(wrapper.text()).toContain('Low priority item')
    expect(wrapper.text()).toContain('High priority item')
    expect(wrapper.text()).toContain('Medium priority item')
  })

  it('sorts recommendations by priority, high first', () => {
    const wrapper = mount(AdviceList, { props: { advice: ADVICE } })

    const titles = wrapper.findAll('h3').map((el) => el.text())
    expect(titles).toEqual(['High priority item', 'Medium priority item', 'Low priority item'])
  })

  it('shows the mock-data notice only when source is mock', () => {
    const mockAdvice = { ...ADVICE, source: 'mock' as const }
    const llmAdvice = { ...ADVICE, source: 'llm' as const }

    expect(mount(AdviceList, { props: { advice: mockAdvice } }).text()).toContain('mock advice')
    expect(mount(AdviceList, { props: { advice: llmAdvice } }).text()).not.toContain('mock advice')
  })

  it('formats savings only when estimated_annual_savings_eur is present', () => {
    const wrapper = mount(AdviceList, { props: { advice: ADVICE } })

    expect(wrapper.text()).toContain('~€50/year')
    expect(wrapper.text()).toContain('~€200/year')
  })
})
