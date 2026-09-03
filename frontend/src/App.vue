<script setup lang="ts">
import { storeToRefs } from 'pinia'
import AdviceList from './components/AdviceList.vue'
import HomeForm from './components/HomeForm.vue'
import { useHomeStore } from './stores/home'
import type { HomeCreate } from './types/home'

const store = useHomeStore()
const { advice, error, isSubmittingHome, isGeneratingAdvice } = storeToRefs(store)

function handleSubmit(payload: HomeCreate) {
  store.submitHomeAndGetAdvice(payload)
}
</script>

<template>
  <main>
    <header class="page-header">
      <h1>Home Energy Advisor</h1>
      <p>Describe your home and get AI-generated energy efficiency recommendations.</p>
    </header>

    <div class="layout">
      <HomeForm :submitting="isSubmittingHome" @submit="handleSubmit" />

      <div class="results">
        <p v-if="isGeneratingAdvice" class="status">Generating recommendations…</p>
        <p v-else-if="error" class="status error" role="alert">{{ error }}</p>
        <AdviceList v-else-if="advice" :advice="advice" />
        <p v-else class="status placeholder">
          Fill in your home details to get personalized recommendations.
        </p>
      </div>
    </div>
  </main>
</template>

<style scoped>
main {
  max-width: 64rem;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
  font-family:
    system-ui,
    -apple-system,
    'Segoe UI',
    sans-serif;
  color: #1a1a1a;
}

.page-header h1 {
  margin: 0 0 0.25rem;
  font-size: 1.75rem;
}

.page-header p {
  margin: 0 0 2rem;
  color: #555;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 20rem) minmax(0, 1fr);
  gap: 2.5rem;
  align-items: start;
}

@media (max-width: 55rem) {
  .layout {
    grid-template-columns: 1fr;
  }
}

.status {
  color: #555;
}

.status.error {
  color: #c0392b;
  font-weight: 600;
}

.status.placeholder {
  color: #888;
  font-style: italic;
}
</style>
