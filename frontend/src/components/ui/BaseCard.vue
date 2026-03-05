<template>
  <article class="card" :class="{ 'card--tint': tinted }">
    <slot />
  </article>
</template>

<script setup lang="ts">
defineProps<{
  tinted?: boolean
}>()
</script>
