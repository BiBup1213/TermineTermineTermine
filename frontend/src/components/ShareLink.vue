<template>
  <div class="card inline-card">
    <div>
      <div class="label">Share link</div>
      <div class="mono">{{ link }}</div>
    </div>
    <button class="btn" type="button" @click="copy">Kopieren</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { showToast } from '../composables/toast'

const props = defineProps<{ pollId: string }>()

const link = computed(() => `${window.location.origin}/p/${props.pollId}`)

async function copy() {
  await navigator.clipboard.writeText(link.value)
  showToast('Share-Link kopiert')
}
</script>
