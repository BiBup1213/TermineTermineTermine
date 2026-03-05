<template>
  <div class="card inline-card">
    <BaseInput id="share-link" :model-value="link" label="Share link" readonly />
    <BaseButton @click="copy">Kopieren</BaseButton>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { showToast } from '../composables/toast'
import BaseButton from './ui/BaseButton.vue'
import BaseInput from './ui/BaseInput.vue'

const props = defineProps<{ pollId: string }>()

const link = computed(() => `${window.location.origin}/p/${props.pollId}`)

async function copy() {
  await navigator.clipboard.writeText(link.value)
  showToast('Share-Link kopiert')
}
</script>
