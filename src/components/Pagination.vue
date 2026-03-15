<script setup>
const props = defineProps({
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 }
})

const emit = defineEmits(['change'])

function goTo(page) {
  if (page < 1 || page > props.totalPages || page === props.currentPage) return
  emit('change', page)
}
</script>

<template>
  <div class="join" role="navigation" aria-label="pagination">
    <button class="join-item btn" :disabled="currentPage === 1" @click="goTo(currentPage - 1)">قبلی</button>
    <button class="join-item btn btn-active" disabled>{{ currentPage }} / {{ totalPages }}</button>
    <button class="join-item btn" :disabled="currentPage === totalPages" @click="goTo(currentPage + 1)">بعدی</button>
  </div>
</template>
