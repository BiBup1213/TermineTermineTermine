<template>
  <section v-if="poll" class="stack-lg">
    <BaseCard>
      <div class="stack">
        <h1>{{ poll.title }}</h1>
        <p v-if="poll.description" class="muted">{{ poll.description }}</p>
        <p class="muted">
          Zeitraum: {{ formatDateDE(poll.date_range_from) }} bis {{ formatDateDE(poll.date_range_to) }} ({{ poll.timezone }})
        </p>
        <ShareLink :poll-id="poll.id" />
        <div class="actions">
          <RouterLink class="btn btn--ghost" :to="`/p/${poll.id}/results`">Zu den Ergebnissen</RouterLink>
        </div>
      </div>
    </BaseCard>

    <BaseCard v-if="adminTokenShown">
      <div class="stack">
        <strong>Admin-Token (nur jetzt sichtbar)</strong>
        <div class="mono token">{{ oneTimeAdminToken }}</div>
        <div class="actions">
          <BaseButton @click="copyAdminToken">Admin-Token kopieren</BaseButton>
        </div>
      </div>
    </BaseCard>

    <BaseCard v-if="!isAdmin">
      <div class="stack">
        <button class="admin-toggle" type="button" @click="showAdminEntry = !showAdminEntry">
          {{ showAdminEntry ? 'Admin schließen' : 'Admin öffnen' }}
        </button>

        <div v-if="showAdminEntry" class="stack">
          <BaseInput
            id="admin-token"
            v-model.trim="adminToken"
            label="Admin-Token"
            placeholder="Token eingeben"
            hint="Nur notwendig für Kandidatentage und Sperren/Entsperren"
          />
          <div class="actions">
            <BaseButton @click="activateAdminFromInput">Admin-Modus aktivieren</BaseButton>
          </div>
          <p v-if="adminError" class="warning">{{ adminError }}</p>
        </div>
      </div>
    </BaseCard>

    <BaseCard v-if="isAdmin" tinted>
      <div class="stack-lg">
        <div class="actions actions--between">
          <h2>Admin-Bereich</h2>
          <button type="button" class="btn-link" @click="leaveAdminMode">Admin schließen</button>
        </div>
        <p class="muted">Kandidatentage auswählen</p>

        <CalendarMonth
          :range-from="poll.date_range_from"
          :range-to="poll.date_range_to"
          :candidate-days="poll.candidate_days"
          :selected-days="selectedCandidateDays"
          mode="admin"
          @day-click="toggleCandidateDay"
        />

        <div class="actions">
          <BaseButton @click="saveCandidateDays">Candidate Days speichern</BaseButton>
          <BaseButton variant="ghost" @click="toggleLock">
            {{ poll.is_locked ? 'Entsperren' : 'Sperren' }}
          </BaseButton>
        </div>
      </div>
    </BaseCard>

    <BaseCard>
      <div class="stack-lg">
        <div class="stack">
          <h2>Abstimmung</h2>
          <p v-if="poll.is_locked" class="warning">Poll ist gesperrt. Nur Lesen.</p>
        </div>

        <BaseInput
          id="participant-name"
          v-model.trim="participantName"
          label="Dein Anzeigename"
          :disabled="poll.is_locked"
          required
        />

        <VoteLegend />

        <CalendarMonth
          :range-from="poll.date_range_from"
          :range-to="poll.date_range_to"
          :candidate-days="poll.candidate_days"
          :vote-choices="voteChoices"
          mode="vote"
          @day-click="cycleVoteChoice"
        />

        <div class="sticky-save">
          <div class="actions actions--between">
            <span class="help-text">Deine Auswahl bleibt lokal gespeichert, bis du speicherst.</span>
            <BaseButton :disabled="poll.is_locked" @click="saveVote">Stimme speichern</BaseButton>
          </div>
        </div>
      </div>
    </BaseCard>
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
import BaseButton from '../components/ui/BaseButton.vue'
import BaseCard from '../components/ui/BaseCard.vue'
import BaseInput from '../components/ui/BaseInput.vue'
import { showToast } from '../composables/toast'
import { clearStoredAdminToken, getStoredAdminToken, setStoredAdminToken } from '../utils/adminToken'
import { formatDateDE } from '../utils/dateFormat'

const route = useRoute()
const pollId = route.params.pollId as string

const poll = ref<PollResponse | null>(null)
const adminToken = ref('')
const adminTokenShown = ref(false)
const oneTimeAdminToken = ref('')
const isAdmin = ref(false)
const showAdminEntry = ref(false)
const adminError = ref('')
const selectedCandidateDays = ref<string[]>([])
const participantName = ref('')
const voteChoices = ref<Record<string, VoteChoice>>({})

function participantTokenKey(): string {
  return `participant-token-${pollId}`
}

function getParticipantToken(): string {
  const existing = localStorage.getItem(participantTokenKey())
  if (existing) return existing
  const generated = crypto.randomUUID()
  localStorage.setItem(participantTokenKey(), generated)
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

function handleAdminError(err: unknown) {
  const message = (err as Error).message
  const authError = message.includes('401') || message.toLowerCase().includes('unauthorized')

  if (authError) {
    isAdmin.value = false
    clearStoredAdminToken(pollId)
    adminError.value = 'Admin-Token ungültig oder abgelaufen.'
    showAdminEntry.value = true
  }

  showToast(message)
}

async function validateAdminToken(token: string, showSuccessToast = true): Promise<boolean> {
  if (!poll.value) return false
  if (!token) {
    adminError.value = 'Bitte Admin-Token eingeben.'
    return false
  }

  try {
    adminError.value = ''
    poll.value = await patchPoll(pollId, { is_locked: poll.value.is_locked }, token)
    isAdmin.value = true
    adminToken.value = token
    setStoredAdminToken(pollId, token)
    showAdminEntry.value = false
    if (showSuccessToast) showToast('Admin-Modus aktiviert')
    return true
  } catch (err) {
    handleAdminError(err)
    return false
  }
}

async function activateAdminFromInput() {
  await validateAdminToken(adminToken.value, true)
}

function leaveAdminMode() {
  isAdmin.value = false
  showAdminEntry.value = false
  adminToken.value = ''
  adminError.value = ''
}

async function saveCandidateDays() {
  if (!poll.value || !isAdmin.value || !adminToken.value) {
    showToast('Admin-Modus ist nicht aktiv')
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
    handleAdminError(err)
  }
}

async function toggleLock() {
  if (!poll.value || !isAdmin.value || !adminToken.value) {
    showToast('Admin-Modus ist nicht aktiv')
    return
  }

  try {
    poll.value = await patchPoll(pollId, { is_locked: !poll.value.is_locked }, adminToken.value)
    showToast(poll.value.is_locked ? 'Poll gesperrt' : 'Poll entsperrt')
  } catch (err) {
    handleAdminError(err)
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
  if (!oneTimeAdminToken.value) return
  await navigator.clipboard.writeText(oneTimeAdminToken.value)
  showToast('Admin-Token kopiert')
}

function queryAdminToken(): string {
  const adminParam = route.query.admin
  if (typeof adminParam === 'string') return adminParam.trim()
  if (Array.isArray(adminParam) && adminParam.length > 0) return adminParam[0].trim()
  return ''
}

onMounted(async () => {
  await loadPoll()

  const oneTimeToken = sessionStorage.getItem(`admin-token-${pollId}`) ?? ''
  if (oneTimeToken) {
    oneTimeAdminToken.value = oneTimeToken
    adminTokenShown.value = true
    sessionStorage.removeItem(`admin-token-${pollId}`)
  }

  const tokenFromQuery = queryAdminToken()
  const tokenFromStorage = getStoredAdminToken(pollId)
  const candidateToken = tokenFromQuery || oneTimeToken || tokenFromStorage

  if (candidateToken) {
    adminToken.value = candidateToken
    const success = await validateAdminToken(candidateToken, false)
    if (!success && oneTimeToken) {
      showAdminEntry.value = true
      adminToken.value = oneTimeToken
    }
  }
})
</script>
