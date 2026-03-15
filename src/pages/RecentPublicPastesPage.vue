<script setup>
import { onMounted, ref } from 'vue'
import PasteCard from '@/components/PasteCard.vue'
import Pagination from '@/components/Pagination.vue'
import AlertMessage from '@/components/AlertMessage.vue'
import { getRecentPastesRequest } from '@/services/api/pastes'

const loading = ref(false)
const error = ref('')
const items = ref([])
const currentPage = ref(1)
const totalPages = ref(1)

function normalizeRecentResponse(body) {
  const list = body.data || []
  const pagination = body.pagination || {}
  return {
    items: list.map((item) => ({
      ...item,
      id: item.slug,
      content: item.content || ''
    })),
    currentPage: pagination.page || 1,
    totalPages: pagination.pages || 1
  }
}

async function fetchRecent(page = 1) {
  loading.value = true
  error.value = ''
  try {
    const body = await getRecentPastesRequest(page, 10)
    const normalized = normalizeRecentResponse(body)
    items.value = normalized.items
    currentPage.value = normalized.currentPage
    totalPages.value = normalized.totalPages
  } catch (err) {
    error.value = err?.response?.data?.error?.message || 'خطا در دریافت لیست پیست‌ها.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecent(1)
})
</script>

<template>
  <section class="space-y-5">
    <header class="panel-soft">
      <h1 class="text-xl md:text-2xl font-bold">پیست‌های عمومی اخیر</h1>
      <p class="mt-2 text-sm opacity-75">آخرین پیست‌های عمومی منتشرشده را مرور کنید.</p>
    </header>

    <div v-if="loading" class="flex justify-center p-8">
      <span class="loading loading-spinner loading-lg" />
    </div>

    <AlertMessage v-else-if="error" :message="error" type="error" />

    <template v-else>
      <div v-if="!items.length" class="alert surface">
        <span>فعلا پیست عمومی موجود نیست.</span>
      </div>

      <div v-else class="space-y-4">
        <PasteCard v-for="item in items" :key="item.id" :item="item" />
      </div>

      <div class="pt-1">
        <Pagination :current-page="currentPage" :total-pages="totalPages" @change="fetchRecent" />
      </div>
    </template>
  </section>
</template>
