<template>
  <div :class="cardClasses">
    <header
      v-if="$slots.header"
      class="base-card__header"
    >
      <slot name="header" />
    </header>
    <div class="base-card__body">
      <slot />
    </div>
    <footer
      v-if="$slots.footer"
      class="base-card__footer"
    >
      <slot name="footer" />
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  shadow: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'lg', 'none'].includes(value)
  },
  borderless: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const cardClasses = computed(() => [
  'base-card',
  {
    'base-card--shadow-lg': props.shadow === 'lg',
    'base-card--borderless': props.borderless,
    'base-card--compact': props.compact
  }
])
</script>

<style scoped>
</style>
