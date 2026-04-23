<template>
  <Teleport to="body">
    <Transition name="base-modal__backdrop">
      <div
        v-if="show"
        class="base-modal__backdrop"
        :class="{ 'base-modal__backdrop--closing': closing }"
        @click.self="handleBackdropClick"
      >
        <Transition name="base-modal">
          <div
            v-if="show"
            class="base-modal"
            :class="[modalClasses, { 'base-modal--closing': closing }]"
            role="dialog"
            :aria-modal="show"
            :aria-labelledby="modalId"
            @click.stop
          >
            <header
              v-if="$slots.header || title || showClose"
              class="base-modal__header"
            >
              <h2
                v-if="title"
                :id="modalId"
                class="base-modal__title"
              >
                {{ title }}
              </h2>
              <slot
                v-else
                name="header"
              />
              <button
                v-if="showClose"
                type="button"
                class="base-modal__close"
                :aria-label="closeLabel"
                @click="handleClose"
              >
                <CloseIcon />
              </button>
            </header>
            <div class="base-modal__body">
              <slot />
            </div>
            <footer
              v-if="$slots.footer"
              class="base-modal__footer"
            >
              <slot name="footer" />
            </footer>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { CloseIcon } from './icons'

let modalCount = 0

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl', 'fullscreen'].includes(value)
  },
  closeOnEsc: {
    type: Boolean,
    default: true
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  },
  showClose: {
    type: Boolean,
    default: true
  },
  closeLabel: {
    type: String,
    default: '关闭'
  }
})

const emit = defineEmits(['update:show', 'close'])

const closing = ref(false)
const modalId = computed(() => `base-modal-${modalCount++}`)

const modalClasses = computed(() => [
  `base-modal--${props.size}`
])

const handleClose = () => {
  closing.value = true
  setTimeout(() => {
    emit('update:show', false)
    emit('close')
    closing.value = false
  }, 200)
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    handleClose()
  }
}

const handleKeydown = (event) => {
  if (event.key === 'Escape' && props.closeOnEsc && props.show) {
    handleClose()
  }
}

// 监听显示状态，处理焦点和滚动
watch(() => props.show, async (newVal) => {
  if (newVal) {
    await nextTick()
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
</style>
