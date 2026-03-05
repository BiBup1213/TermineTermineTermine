<template>
  <button
    class="day-cell"
    :class="[`state-${state}`, { disabled }]"
    :disabled="disabled"
    type="button"
    :aria-label="ariaLabel"
    @click="$emit('toggle')"
    @keydown.enter.prevent="$emit('toggle')"
    @keydown.space.prevent="$emit('toggle')"
  >
    <span class="day-num">{{ dayNumber }}</span>
    <span class="symbol" aria-hidden="true">{{ symbol }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  dayNumber: number
  state: 'none' | 'selected' | 'no' | 'maybe' | 'yes'
  disabled?: boolean
  ariaLabel: string
}>()

defineEmits<{ (e: 'toggle'): void }>()

const symbolMap = {
  none: '',
  selected: '✓',
  no: '○',
  maybe: '△',
  yes: '✓'
} as const

const symbol = computed(() => symbolMap[props.state])
</script>
