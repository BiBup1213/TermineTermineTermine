<template>
  <section class="stack">
    <div class="card">
      <h1>Neuen Meetup-Poll erstellen</h1>
      <form class="stack" @submit.prevent="onCreate">
        <label>
          Titel
          <input v-model.trim="form.title" required maxlength="200" />
        </label>

        <label>
          Beschreibung
          <textarea v-model.trim="form.description" rows="3" maxlength="2000" />
        </label>

        <label>
          Zeitzone
          <input v-model="form.timezone" />
        </label>

        <div class="row">
          <label>
            Von
            <input v-model="form.date_range_from" type="date" required />
          </label>
          <label>
            Bis
            <input v-model="form.date_range_to" type="date" required />
          </label>
        </div>

        <button class="btn" type="submit" :disabled="loading">Poll erstellen</button>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createPoll } from '../api/client'
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

async function onCreate() {
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
