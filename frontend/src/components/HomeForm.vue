<script setup lang="ts">
import { reactive } from 'vue'
import {
  HEATING_TYPE_LABELS,
  HEATING_TYPES,
  INSULATION_QUALITY_LABELS,
  INSULATION_QUALITIES,
  type HomeCreate,
} from '../types/home'

const props = defineProps<{
  submitting: boolean
}>()

const emit = defineEmits<{
  submit: [payload: HomeCreate]
}>()

const currentYear = new Date().getFullYear()

const form = reactive({
  size_sqm: '',
  year_built: '',
  heating_type: 'gas' as HomeCreate['heating_type'],
  insulation_quality: 'average' as HomeCreate['insulation_quality'],
  occupants: '',
})

const fieldErrors = reactive<Record<string, string>>({})

function validate(): boolean {
  Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key])

  const size = Number(form.size_sqm)
  if (!form.size_sqm || Number.isNaN(size) || size <= 0) {
    fieldErrors.size_sqm = 'Enter a positive size in square meters.'
  }

  const year = Number(form.year_built)
  if (!form.year_built || Number.isNaN(year) || year < 1800 || year > currentYear) {
    fieldErrors.year_built = `Enter a year between 1800 and ${currentYear}.`
  }

  if (form.occupants !== '') {
    const occupants = Number(form.occupants)
    if (Number.isNaN(occupants) || occupants < 1) {
      fieldErrors.occupants = 'Occupants must be a positive number, or left blank.'
    }
  }

  return Object.keys(fieldErrors).length === 0
}

function handleSubmit() {
  if (!validate()) return

  emit('submit', {
    size_sqm: Number(form.size_sqm),
    year_built: Number(form.year_built),
    heating_type: form.heating_type,
    insulation_quality: form.insulation_quality,
    occupants: form.occupants === '' ? null : Number(form.occupants),
  })
}

defineExpose({ form, fieldErrors, validate })
</script>

<template>
  <form class="home-form" novalidate @submit.prevent="handleSubmit">
    <div class="field">
      <label for="size_sqm">Home size (m²)</label>
      <input
        id="size_sqm"
        v-model="form.size_sqm"
        type="number"
        min="1"
        step="any"
        placeholder="e.g. 120"
        :aria-invalid="!!fieldErrors.size_sqm"
      />
      <p v-if="fieldErrors.size_sqm" class="field-error">{{ fieldErrors.size_sqm }}</p>
    </div>

    <div class="field">
      <label for="year_built">Year built</label>
      <input
        id="year_built"
        v-model="form.year_built"
        type="number"
        min="1800"
        :max="currentYear"
        placeholder="e.g. 1998"
        :aria-invalid="!!fieldErrors.year_built"
      />
      <p v-if="fieldErrors.year_built" class="field-error">{{ fieldErrors.year_built }}</p>
    </div>

    <div class="field">
      <label for="heating_type">Heating type</label>
      <select id="heating_type" v-model="form.heating_type">
        <option v-for="type in HEATING_TYPES" :key="type" :value="type">
          {{ HEATING_TYPE_LABELS[type] }}
        </option>
      </select>
    </div>

    <div class="field">
      <label for="insulation_quality">Insulation quality</label>
      <select id="insulation_quality" v-model="form.insulation_quality">
        <option v-for="quality in INSULATION_QUALITIES" :key="quality" :value="quality">
          {{ INSULATION_QUALITY_LABELS[quality] }}
        </option>
      </select>
    </div>

    <div class="field">
      <label for="occupants">Occupants (optional)</label>
      <input
        id="occupants"
        v-model="form.occupants"
        type="number"
        min="1"
        placeholder="e.g. 3"
        :aria-invalid="!!fieldErrors.occupants"
      />
      <p v-if="fieldErrors.occupants" class="field-error">{{ fieldErrors.occupants }}</p>
    </div>

    <button type="submit" :disabled="props.submitting">
      {{ props.submitting ? 'Saving…' : 'Get energy advice' }}
    </button>
  </form>
</template>

<style scoped>
.home-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 28rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

label {
  font-weight: 600;
  font-size: 0.9rem;
}

input,
select {
  padding: 0.5rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}

input[aria-invalid='true'] {
  border-color: #c0392b;
}

.field-error {
  color: #c0392b;
  font-size: 0.85rem;
  margin: 0;
}

button {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 6px;
  background: #2c7a4b;
  color: white;
  font-size: 1rem;
  cursor: pointer;
}

button:disabled {
  background: #9bb8a9;
  cursor: not-allowed;
}
</style>
