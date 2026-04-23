<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <span
      v-if="loading"
      class="base-button__spinner"
      aria-hidden="true"
    />
    <span
      v-if="icon && !loading"
      class="base-button__icon"
      aria-hidden="true"
    >
      <component :is="icon" />
    </span>
    <span
      v-if="$slots.default"
      class="base-button__content"
    >
      <slot />
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'button',
    validator: (value) => ['button', 'submit', 'reset'].includes(value)
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'warning', 'danger', 'ghost'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  },
  icon: {
    type: [String, Object],
    default: null
  }
})

const emit = defineEmits(['click'])

const buttonClasses = computed(() => [
  'base-button',
  `base-button--${props.variant}`,
  `base-button--${props.size}`,
  {
    'base-button--block': props.block,
    'base-button--loading': props.loading
  }
])

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.base-button__content {
  display: inline-flex;
  align-items: center;
}

.base-button__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
