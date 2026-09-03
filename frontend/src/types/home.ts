// Mirrors the backend's Pydantic schemas (backend/app/schemas/home.py) and enums
export const HEATING_TYPES = [
  'gas',
  'oil',
  'electric',
  'heat_pump',
  'district_heating',
  'other',
] as const
export type HeatingType = (typeof HEATING_TYPES)[number]

export const INSULATION_QUALITIES = ['poor', 'average', 'good', 'excellent'] as const
export type InsulationQuality = (typeof INSULATION_QUALITIES)[number]

export type RecommendationPriority = 'high' | 'medium' | 'low'

export interface HomeCreate {
  size_sqm: number
  year_built: number
  heating_type: HeatingType
  insulation_quality: InsulationQuality
  occupants: number | null
}

export interface Home {
  id: string
  size_sqm: number
  year_built: number
  heating_type: HeatingType
  insulation_quality: InsulationQuality
  occupants: number | null
  created_at: string
}

export interface Recommendation {
  title: string
  description: string
  priority: RecommendationPriority
  category: string
  estimated_annual_savings_eur: number | null
}

export interface AdviceResponse {
  home_id: string
  summary: string
  recommendations: Recommendation[]
  generated_at: string
  source: 'llm' | 'mock'
}

export const HEATING_TYPE_LABELS: Record<HeatingType, string> = {
  gas: 'Gas',
  oil: 'Oil',
  electric: 'Electric',
  heat_pump: 'Heat pump',
  district_heating: 'District heating',
  other: 'Other',
}

export const INSULATION_QUALITY_LABELS: Record<InsulationQuality, string> = {
  poor: 'Poor',
  average: 'Average',
  good: 'Good',
  excellent: 'Excellent',
}
