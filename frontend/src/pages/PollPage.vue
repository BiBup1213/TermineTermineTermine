<template>
  <section v-if="poll" class="stack">
    <div class="card">
      <h1>{{ poll.title }}</h1>
      <p v-if="poll.description">{{ poll.description }}</p>
      <p class="muted">Zeitraum: {{ poll.date_range_from }} bis {{ poll.date_range_to }} ({{ poll.timezone }})</p>
      <ShareLink :poll-id="poll.id" />
      <RouterLink class="btn ghost" :to="`/p/${poll.id}/results`">Zu den Ergebnissen</RouterLink>
    </div>

    <div v-if="adminTokenShown" class="card">
      <strong>Admin-Token (nur jetzt sichtbar)</strong>
      <div class="mono token">{{ adminToken }}</div>
      <button class="btn" @click="copyAdminToken">Admin-Token kopieren</button>
    </div>

    <div class="card stack">
      <h2>Admin-Bereich</h2>
      <label>
        Admin-Token
        <input v-model.trim="adminToken" placeholder="Token eingeben" />
      </label>

      <div class="row">
        <button class="btn" @click="saveCandidateDays">Candidate Days speichern</button>
        <button class="btn ghost" @click="toggleLock">{{ poll.is_locked ? 'Entsperren' : 'Sperren' }}</button>
      </div>

      <CalendarMonth
        :range-from="poll.date_range_from"
        :range-to="poll.date_range_to"
        :candidate-days="poll.candidate_days"
        :selected-days="selectedCandidateDays"
        mode="admin"
        @day-click="toggleCandidateDay"
      />
    </div>

    <div class="card stack">
      <h2>Abstimmung</h2>
      <p v-if="poll.is_locked" class="warning">Poll ist gesperrt. Nur Lesen.</p>

      <label>
        Dein Anzeigename
        <input v-model.trim="participantName" :disabled="poll.is_locked" required />
      </label>

      <VoteLegend />

      <CalendarMonth
        :range-from="poll.date_range_from"
        :range-to="poll.date_range_to"
        :candidate-days="poll.candidate_days"
        :vote-choices="voteChoices"
        mode="vote"
        @day-click="cycleVoteChoice"
      />

      <button class="btn" :disabled="poll.is_locked" @click="saveVote">Stimme speichern</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getPoll, patchPoll, submitVote } from '../api/client'
import type { PollResponse, VoteChoice } from '../api/types'
import CalendarMonth from '../components/CalendarMonth.vue'
import ShareLink from '../components/ShareLink.vue'
import VoteLegend from '../components/VoteLegend.vue'
import { showToast } from '../composables/toast'

const route = useRoute()
const pollId = route.params.pollId as string

const poll = ref<PollResponse | null>(null)
const adminToken = ref('')
const adminTokenShown = ref(false)
const selectedCandidateDays = ref<string[]>([])
const participantName = ref('')
const voteChoices = ref<Record<string, VoteChoice>>({})

function tokenKey(): string {
  return `participant-token-${pollId}`
}

function getParticipantToken(): string {
  const existing = localStorage.getItem(tokenKey())
  if (existing) return existing
  const generated = crypto.randomUUID()
  localStorage.setItem(tokenKey(), generated)
  return generated
}

function cycle(current: VoteChoice): VoteChoice {
  if (current === 'no') return 'maybe'
  if (current === 'maybe') return 'yes'
  return 'no'
}

function cycleVoteChoice(day: string) {
  if (!poll.value || poll.value.is_locked) return
  const current = voteChoices.value[day] ?? 'no'
  voteChoices.value = {
    ...voteChoices.value,
    [day]: cycle(current)
  }
}

function toggleCandidateDay(day: string) {
  if (!selectedCandidateDays.value.includes(day)) {
    selectedCandidateDays.value = [...selectedCandidateDays.value, day].sort()
    return
  }
  selectedCandidateDays.value = selectedCandidateDays.value.filter((d) => d !== day)
}

function initVoteDays(candidateDays: string[]) {
  const next: Record<string, VoteChoice> = {}
  for (const day of candidateDays) {
    next[day] = voteChoices.value[day] ?? 'no'
  }
  voteChoices.value = next
}

async function loadPoll() {
  try {
    poll.value = await getPoll(pollId)
    selectedCandidateDays.value = [...poll.value.candidate_days]
    initVoteDays(poll.value.candidate_days)
  } catch (err) {
    showToast((err as Error).message)
  }
}

async function saveCandidateDays() {
  if (!adminToken.value) {
    showToast('Admin-Token fehlt')
    return
  }
  try {
    poll.value = await patchPoll(
      pollId,
      { candidate_days: selectedCandidateDays.value.sort() },
      adminToken.value
    )
    initVoteDays(poll.value.candidate_days)
    showToast('Candidate Days gespeichert')
  } catch (err) {
    showToast((err as Error).message)
  }
}

async function toggleLock() {
  if (!poll.value) return
  if (!adminToken.value) {
    showToast('Admin-Token fehlt')
    return
  }
  try {
    poll.value = await patchPoll(pollId, { is_locked: !poll.value.is_locked }, adminToken.value)
    showToast(poll.value.is_locked ? 'Poll gesperrt' : 'Poll entsperrt')
  } catch (err) {
    showToast((err as Error).message)
  }
}

async function saveVote() {
  if (!poll.value) return
  if (!participantName.value.trim()) {
    showToast('Bitte Anzeigenamen eingeben')
    return
  }

  try {
    await submitVote(pollId, {
      participant_name: participantName.value,
      participant_token: getParticipantToken(),
      choices: poll.value.candidate_days.map((day) => ({ day, choice: voteChoices.value[day] ?? 'no' }))
    })
    showToast('Stimme gespeichert')
  } catch (err) {
    showToast((err as Error).message)
  }
}

async function copyAdminToken() {
  if (!adminToken.value) return
  await navigator.clipboard.writeText(adminToken.value)
  showToast('Admin-Token kopiert')
}

onMounted(async () => {
  const sessionToken = sessionStorage.getItem(`admin-token-${pollId}`)
  if (sessionToken) {
    adminToken.value = sessionToken
    adminTokenShown.value = true
    sessionStorage.removeItem(`admin-token-${pollId}`)
  }
  await loadPoll()
})
</script>
