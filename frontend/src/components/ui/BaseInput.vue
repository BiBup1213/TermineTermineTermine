<template>
  <label class="field" :for="id">
    <span class="field-label">{{ label }}</span>
    <input
      :id="id"
      class="input"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :maxlength="maxlength"
      :disabled="disabled"
      :readonly="readonly"
      @input="onInput"
    />
    <span v-if="hint" class="field-hint">{{ hint }}</span>
  </label>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    id?: string
    modelValue: string
    label: string
    type?: string
    placeholder?: string
    required?: boolean
    maxlength?: number
    disabled?: boolean
    readonly?: boolean
    hint?: string
  }>(),
  {
    id: undefined,
    type: 'text',
    placeholder: '',
    required: false,
    maxlength: undefined,
    disabled: false,
    readonly: false,
    hint: ''
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>
