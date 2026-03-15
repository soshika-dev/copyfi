<script setup>
defineProps({
  type: {
    type: String,
    default: 'error'
  },
  message: {
    type: String,
    required: true
  }
})
</script>

<template>
  <div class="alert" :class="`alert-${type}`" role="alert">
    <span>{{ message }}</span>
  </div>
</template>
