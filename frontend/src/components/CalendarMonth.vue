<template>
  <div class="card">
    <div class="calendar-head">
      <button class="btn ghost" :disabled="!canPrev" @click="stepMonth(-1)">←</button>
      <strong>{{ monthTitle }}</strong>
      <button class="btn ghost" :disabled="!canNext" @click="stepMonth(1)">→</button>
    </div>

    <div class="weekday-row">
      <span v-for="wd in weekdays" :key="wd">{{ wd }}</span>
    </div>

    <div class="grid">
      <div v-for="(cell, idx) in cells" :key="idx" class="grid-cell">
        <DayCell
          v-if="cell"
          :day-number="cell.dayNumber"
          :state="cell.state"
          :disabled="cell.disabled"
          :aria-label="cell.ariaLabel"
          @toggle="emit('day-click', cell.iso)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import DayCell from './DayCell.vue'
import type { VoteChoice } from '../api/types'
import { formatDateDE } from '../utils/dateFormat'

const props = defineProps<{
  rangeFrom: string
  rangeTo: string
  candidateDays: string[]
  selectedDays?: string[]
  voteChoices?: Record<string, VoteChoice>
  mode: 'admin' | 'vote'
}>()

const emit = defineEmits<{ (e: 'day-click', day: string): void }>()

const weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

function parseDate(iso: string): Date {
  return new Date(`${iso}T00:00:00`)
}

function toIso(d: Date): string {
  const y = d.getFullYear()
  const m = `${d.getMonth() + 1}`.padStart(2, '0')
  const day = `${d.getDate()}`.padStart(2, '0')
  return `${y}-${m}-${day}`
}

const fromDate = computed(() => parseDate(props.rangeFrom))
const toDate = computed(() => parseDate(props.rangeTo))
const currentMonth = ref(new Date(fromDate.value.getFullYear(), fromDate.value.getMonth(), 1))

watch(
  () => [props.rangeFrom, props.rangeTo],
  () => {
    currentMonth.value = new Date(fromDate.value.getFullYear(), fromDate.value.getMonth(), 1)
  }
)

const canPrev = computed(() => {
  const prev = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1)
  return prev >= new Date(fromDate.value.getFullYear(), fromDate.value.getMonth(), 1)
})

const canNext = computed(() => {
  const next = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1)
  return next <= new Date(toDate.value.getFullYear(), toDate.value.getMonth(), 1)
})

const monthTitle = computed(() =>
  currentMonth.value.toLocaleDateString('de-DE', { month: 'long', year: 'numeric' })
)

function stepMonth(delta: number) {
  const next = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + delta, 1)
  const min = new Date(fromDate.value.getFullYear(), fromDate.value.getMonth(), 1)
  const max = new Date(toDate.value.getFullYear(), toDate.value.getMonth(), 1)
  if (next >= min && next <= max) {
    currentMonth.value = next
  }
}

const cells = computed(() => {
  const first = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth(), 1)
  const last = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 0)
  const startOffset = (first.getDay() + 6) % 7
  const totalDays = last.getDate()

  const candidate = new Set(props.candidateDays)
  const selected = new Set(props.selectedDays ?? [])
  const entries: Array<
    | null
    | {
        iso: string
        dayNumber: number
        state: 'none' | 'selected' | 'no' | 'maybe' | 'yes'
        disabled: boolean
        ariaLabel: string
      }
  > = []

  for (let i = 0; i < startOffset; i += 1) {
    entries.push(null)
  }

  for (let day = 1; day <= totalDays; day += 1) {
    const d = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth(), day)
    const iso = toIso(d)
    const inRange = d >= fromDate.value && d <= toDate.value

    let state: 'none' | 'selected' | 'no' | 'maybe' | 'yes' = 'none'
    let disabled = !inRange

    if (props.mode === 'admin') {
      state = selected.has(iso) ? 'selected' : 'none'
      disabled = !inRange
    } else {
      disabled = !candidate.has(iso)
      const c = props.voteChoices?.[iso]
      state = c === 'yes' ? 'yes' : c === 'maybe' ? 'maybe' : candidate.has(iso) ? 'no' : 'none'
    }

    entries.push({
      iso,
      dayNumber: day,
      state,
      disabled,
      ariaLabel: `${formatDateDE(iso)} ${state}`
    })
  }

  while (entries.length % 7 !== 0) {
    entries.push(null)
  }

  return entries
})
</script>
