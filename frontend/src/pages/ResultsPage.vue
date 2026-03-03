<template>
  <section class="stack" v-if="results">
    <div class="card">
      <h1>Ergebnisse: {{ results.title }}</h1>
      <p v-if="results.is_locked" class="muted">Status: Gesperrt (read-only)</p>
      <RouterLink class="btn ghost" :to="`/p/${results.poll_id}`">Zurück zur Abstimmung</RouterLink>
    </div>

    <div class="card">
      <h2>Sortierte Tage</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Tag</th>
            <th>Score</th>
            <th>Ja</th>
            <th>Vielleicht</th>
            <th>Nein</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in results.sorted_days" :key="d.day" :class="{ top: d.is_top }">
            <td>{{ d.day }} <span v-if="d.is_top">⭐</span></td>
            <td>{{ d.score }}</td>
            <td>{{ d.yes }}</td>
            <td>{{ d.maybe }}</td>
            <td>{{ d.no }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>Matrix</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Teilnehmer</th>
            <th v-for="d in orderedDays" :key="d">{{ d }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in results.participants" :key="p.participant_name">
            <td>{{ p.participant_name }}</td>
            <td v-for="d in orderedDays" :key="`${p.participant_name}-${d}`">{{ symbol(p.choices[d]) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getResults } from '../api/client'
import type { ResultsResponse, VoteChoice } from '../api/types'
import { showToast } from '../composables/toast'

const route = useRoute()
const pollId = route.params.pollId as string
const results = ref<ResultsResponse | null>(null)

const orderedDays = computed(() => results.value?.sorted_days.map((d) => d.day) ?? [])

function symbol(choice: VoteChoice | undefined): string {
  if (choice === 'yes') return '● Ja'
  if (choice === 'maybe') return '△ Vielleicht'
  return '○ Nein'
}

onMounted(async () => {
  try {
    results.value = await getResults(pollId)
  } catch (err) {
    showToast((err as Error).message)
  }
})
</script>
