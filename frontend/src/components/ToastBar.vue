<template>
  <div v-if="toastState.visible" class="toast" role="status" aria-live="polite">
    {{ toastState.message }}
  </div>
</template>

<script setup lang="ts">
import { toastState } from '../composables/toast'
</script>
