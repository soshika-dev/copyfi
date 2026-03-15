<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import PasteForm from '@/components/PasteForm.vue'
import { createPasteRequest } from '@/services/api/pastes'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const uiStore = useUiStore()

const loading = ref(false)

async function onSubmit(payload) {
  loading.value = true
  try {
    const data = await createPasteRequest(payload)
    const pastePath = `/p/${data.slug}`
    const pasteUrl = `${window.location.origin}${pastePath}`

    uiStore.showToast('پیست با موفقیت ایجاد شد.', 'success', 6500, {
      link: pasteUrl,
      linkLabel: 'لینک پیست'
    })

    router.push(pastePath)
  } catch (err) {
    const message = err?.response?.data?.error?.message || 'خطا در ایجاد پیست. دوباره تلاش کنید.'
    uiStore.showToast(message, 'error', 3200)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="space-y-5">
    <PasteForm :loading="loading" @submit="onSubmit" />
  </section>
</template>
