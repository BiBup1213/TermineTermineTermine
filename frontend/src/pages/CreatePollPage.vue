<template>
  <section class="stack-lg">
    <BaseCard>
      <div class="stack-lg">
        <div class="stack">
          <h1>Neuen Meetup-Poll erstellen</h1>
          <p class="muted">Plane einen Zeitraum, teile den Link und sammle schnell alle Stimmen.</p>
        </div>

        <form class="stack-lg" @submit.prevent="onCreate">
          <BaseInput
            id="poll-title"
            v-model="form.title"
            label="Titel"
            hint="Pflichtfeld"
            required
            :maxlength="200"
          />

          <div class="stack">
            <button
              type="button"
              class="admin-toggle"
              @click="showDescription = !showDescription"
              :aria-expanded="showDescription"
              aria-controls="poll-description"
            >
              {{ showDescription ? 'Beschreibung ausblenden' : 'Add description' }}
            </button>
            <label v-if="showDescription" class="field" for="poll-description">
              <span class="field-label">Beschreibung</span>
              <textarea
                id="poll-description"
                v-model.trim="form.description"
                rows="4"
                maxlength="2000"
                placeholder="Optional: Kontext oder Hinweise für alle Teilnehmenden"
              />
            </label>
          </div>

          <label class="field" for="timezone">
            <span class="field-label">Zeitzone</span>
            <select id="timezone" v-model="form.timezone">
              <option value="Europe/Berlin">Europe/Berlin</option>
              <option value="Europe/Vienna">Europe/Vienna</option>
              <option value="Europe/Zurich">Europe/Zurich</option>
              <option value="UTC">UTC</option>
            </select>
            <span class="field-hint">Standard ist Europe/Berlin.</span>
          </label>

          <div class="row row-2">
            <BaseInput
              id="date-from"
              v-model="form.date_range_from"
              type="date"
              label="Von"
              hint="Pflichtfeld"
              required
            />
            <BaseInput
              id="date-to"
              v-model="form.date_range_to"
              type="date"
              label="Bis"
              hint="Pflichtfeld"
              required
            />
          </div>

          <div class="actions actions--between">
            <span class="help-text"><span class="req">*</span> Pflichtfelder müssen ausgefüllt sein.</span>
            <BaseButton type="submit" :disabled="loading" block-mobile>
              {{ loading ? 'Erstelle Poll...' : 'Poll erstellen' }}
            </BaseButton>
          </div>
        </form>
      </div>
    </BaseCard>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createPoll } from '../api/client'
import BaseButton from '../components/ui/BaseButton.vue'
import BaseCard from '../components/ui/BaseCard.vue'
import BaseInput from '../components/ui/BaseInput.vue'
import { showToast } from '../composables/toast'

const router = useRouter()
const today = new Date().toISOString().slice(0, 10)

const form = reactive({
  title: '',
  description: '',
  timezone: 'Europe/Berlin',
  date_range_from: today,
  date_range_to: today
})

const loading = ref(false)
const showDescription = ref(false)

async function onCreate() {
  if (form.date_range_to < form.date_range_from) {
    showToast('"Bis" muss am gleichen oder einem späteren Datum liegen')
    return
  }

  try {
    loading.value = true
    const res = await createPoll(form)
    sessionStorage.setItem(`admin-token-${res.poll_id}`, res.admin_token)
    showToast('Poll erstellt. Admin-Token wird einmalig gezeigt.')
    await router.push(`/p/${res.poll_id}`)
  } catch (err) {
    showToast((err as Error).message)
  } finally {
    loading.value = false
  }
}
</script>
