<template>
  <section v-if="results" class="stack-lg">
    <BaseCard>
      <div class="stack">
        <h1>Ergebnisse: {{ results.title }}</h1>
        <p v-if="results.is_locked" class="muted">Status: Gesperrt (read-only)</p>
        <div class="actions">
          <RouterLink class="btn btn--ghost" :to="`/p/${results.poll_id}`">Zurück zur Abstimmung</RouterLink>
        </div>
      </div>
    </BaseCard>

    <BaseCard>
      <div class="stack">
        <h2>Best days</h2>
        <p class="muted">Top 1-3 Tage inklusive Gleichständen, sortiert nach Score.</p>
        <div class="summary-grid">
          <div v-for="day in topDays" :key="day.day" class="top-day">
            <strong>⭐ {{ formatDateDE(day.day) }}</strong>
            <p class="muted">Score: {{ day.score }} (Ja {{ day.yes }}, Vielleicht {{ day.maybe }}, Nein {{ day.no }})</p>
          </div>
        </div>
      </div>
    </BaseCard>

    <BaseCard>
      <div class="stack-lg">
        <h2>Tagesübersicht</h2>
        <div class="summary-grid">
          <div v-for="d in results.sorted_days" :key="d.day" class="day-stats">
            <div class="day-stats-head">
              <strong>{{ formatDateDE(d.day) }}</strong>
              <span class="muted">Score {{ d.score }}</span>
            </div>
            <div class="stacked-bar" role="img" :aria-label="`Ja ${d.yes}, Vielleicht ${d.maybe}, Nein ${d.no}`">
              <span class="segment-yes" :style="{ width: segmentWidth(d.yes, d) }" />
              <span class="segment-maybe" :style="{ width: segmentWidth(d.maybe, d) }" />
              <span class="segment-no" :style="{ width: segmentWidth(d.no, d) }" />
            </div>
            <div class="counts">
              <span>✓ {{ d.yes }}</span>
              <span>△ {{ d.maybe }}</span>
              <span>○ {{ d.no }}</span>
            </div>
          </div>
        </div>
      </div>
    </BaseCard>

    <BaseCard>
      <div class="stack">
        <h2>Matrix</h2>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Teilnehmer</th>
                <th v-for="d in orderedDays" :key="d.raw">{{ d.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in results.participants" :key="p.participant_name">
                <td>{{ p.participant_name }}</td>
                <td
                  v-for="d in orderedDays"
                  :key="`${p.participant_name}-${d.raw}`"
                  :class="cellClass(p.choices[d.raw])"
                >
                  {{ symbol(p.choices[d.raw]) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </BaseCard>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getResults } from '../api/client'
import type { DayResult, ResultsResponse, VoteChoice } from '../api/types'
import BaseCard from '../components/ui/BaseCard.vue'
import { showToast } from '../composables/toast'
import { formatDateDE } from '../utils/dateFormat'

const route = useRoute()
const pollId = route.params.pollId as string
const results = ref<ResultsResponse | null>(null)

const orderedDays = computed(() =>
  (results.value?.sorted_days ?? []).map((d) => ({
    raw: d.day,
    label: formatDateDE(d.day)
  }))
)

const topDays = computed(() => {
  const days = results.value?.sorted_days ?? []
  if (days.length === 0) return []

  const topScore = days[0].score
  const tieDays = days.filter((day) => day.score === topScore)
  if (tieDays.length >= 3) return tieDays

  const rankScores = Array.from(new Set(days.map((day) => day.score)))
  const allowed = new Set(rankScores.slice(0, 3))
  return days.filter((day) => allowed.has(day.score))
})

function symbol(choice: VoteChoice | undefined): string {
  if (choice === 'yes') return '✓'
  if (choice === 'maybe') return '△'
  return '○'
}

function cellClass(choice: VoteChoice | undefined): string {
  if (choice === 'yes') return 'cell-yes'
  if (choice === 'maybe') return 'cell-maybe'
  return 'cell-no'
}

function segmentWidth(value: number, day: DayResult): string {
  const total = day.yes + day.maybe + day.no
  if (total === 0) return '0%'
  return `${Math.round((value / total) * 100)}%`
}

onMounted(async () => {
  try {
    results.value = await getResults(pollId)
  } catch (err) {
    showToast((err as Error).message)
  }
})
</script>
