<script setup lang="ts">
import type { Recommendation } from '../types/home'

defineProps<{
  recommendation: Recommendation
}>()

const priorityLabel: Record<Recommendation['priority'], string> = {
  high: 'High priority',
  medium: 'Medium priority',
  low: 'Low priority',
}
</script>

<template>
  <article class="card" :class="`priority-${recommendation.priority}`">
    <header>
      <span class="badge">{{ priorityLabel[recommendation.priority] }}</span>
      <span class="category">{{ recommendation.category }}</span>
    </header>
    <h3>{{ recommendation.title }}</h3>
    <p>{{ recommendation.description }}</p>
    <p v-if="recommendation.estimated_annual_savings_eur != null" class="savings">
      Est. savings: ~€{{ Math.round(recommendation.estimated_annual_savings_eur) }}/year
    </p>
  </article>
</template>

<style scoped>
.card {
  border: 1px solid #e0e0e0;
  border-left-width: 4px;
  border-radius: 8px;
  padding: 1rem;
  background: white;
}

.priority-high {
  border-left-color: #c0392b;
}

.priority-medium {
  border-left-color: #d68910;
}

.priority-low {
  border-left-color: #7f8c8d;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.badge {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.priority-high .badge {
  color: #c0392b;
}

.priority-medium .badge {
  color: #d68910;
}

.priority-low .badge {
  color: #7f8c8d;
}

.category {
  font-size: 0.75rem;
  color: #888;
  text-transform: capitalize;
}

h3 {
  margin: 0 0 0.35rem;
  font-size: 1.05rem;
}

p {
  margin: 0 0 0.4rem;
  color: #333;
  line-height: 1.4;
}

.savings {
  font-weight: 600;
  color: #2c7a4b;
  margin: 0;
}
</style>
