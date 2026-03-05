<template>
  <button
    :type="type"
    class="btn"
    :class="[
      variant === 'ghost' ? 'btn--ghost' : '',
      variant === 'danger' ? 'btn--danger' : '',
      { 'btn--block-mobile': blockMobile }
    ]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    type?: 'button' | 'submit' | 'reset'
    variant?: 'primary' | 'ghost' | 'danger'
    disabled?: boolean
    blockMobile?: boolean
  }>(),
  {
    type: 'button',
    variant: 'primary',
    disabled: false,
    blockMobile: false
  }
)
</script>
