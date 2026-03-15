<script setup>
const model = defineModel({ type: Boolean, default: false })

const props = defineProps({
  title: { type: String, default: 'تایید' },
  description: { type: String, default: 'آیا مطمئن هستید؟' },
  confirmText: { type: String, default: 'تایید' },
  cancelText: { type: String, default: 'انصراف' }
})

const emit = defineEmits(['confirm'])

function onConfirm() {
  emit('confirm')
  model.value = false
}
</script>

<template>
  <dialog class="modal" :class="{ 'modal-open': model }" aria-modal="true" role="dialog">
    <div class="modal-box">
      <h3 class="text-lg font-bold">{{ props.title }}</h3>
      <p class="py-4">{{ props.description }}</p>
      <div class="modal-action">
        <button class="btn" @click="model = false">{{ props.cancelText }}</button>
        <button class="btn btn-error" @click="onConfirm">{{ props.confirmText }}</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop" @click="model = false">
      <button>close</button>
    </form>
  </dialog>
</template>
