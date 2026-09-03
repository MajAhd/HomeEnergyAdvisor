<script setup lang="ts">
import { computed } from 'vue'
import type { AdviceResponse, RecommendationPriority } from '../types/home'
import RecommendationCard from './RecommendationCard.vue'

const props = defineProps<{
  advice: AdviceResponse
}>()

const PRIORITY_ORDER: Record<RecommendationPriority, number> = { high: 0, medium: 1, low: 2 }
const sortedRecommendations = computed(() =>
  [...props.advice.recommendations].sort(
    (a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority],
  ),
)
</script>

<template>
  <section class="advice">
    <p class="summary">{{ advice.summary }}</p>
    <p v-if="advice.source === 'mock'" class="mock-notice">
      Showing rule-based mock advice (no LLM API key configured on the backend).
    </p>

    <div class="recommendations">
      <RecommendationCard
        v-for="(rec, index) in sortedRecommendations"
        :key="index"
        :recommendation="rec"
      />
    </div>
  </section>
</template>

<style scoped>
.advice {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 40rem;
}

.summary {
  font-size: 1.05rem;
  line-height: 1.5;
}

.mock-notice {
  font-size: 0.85rem;
  color: #8a6d3b;
  background: #fcf3cf;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
</style>
