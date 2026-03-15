<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AlertMessage from '@/components/AlertMessage.vue'
import PasteCard from '@/components/PasteCard.vue'
import { getMyPastesRequest } from '@/services/api/pastes'

const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')
const myPastes = ref([])

const user = computed(() => authStore.user)

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    const body = await getMyPastesRequest(1, 20)
    myPastes.value = (body.data || []).map((item) => ({
      ...item,
      id: item.slug,
      content: item.content || ''
    }))
  } catch (err) {
    error.value = err?.response?.data?.error?.message || 'خطا در دریافت اطلاعات پروفایل.'
  } finally {
    loading.value = false
  }
}

function logout() {
  authStore.logout()
}

onMounted(loadProfile)
</script>

<template>
  <section class="space-y-4">
    <div class="card bg-base-100 border border-base-300">
      <div class="card-body">
        <h1 class="card-title">پروفایل</h1>
        <p><strong>نام کاربری:</strong> {{ user?.username || '-' }}</p>
        <p><strong>ایمیل:</strong> {{ user?.email || '-' }}</p>
        <button class="btn btn-error btn-sm w-fit" @click="logout">خروج</button>
      </div>
    </div>

    <AlertMessage v-if="error" :message="error" type="error" />

    <div class="card bg-base-100 border border-base-300">
      <div class="card-body">
        <h2 class="card-title">پیست‌های من</h2>

        <div v-if="loading" class="flex justify-center p-6">
          <span class="loading loading-spinner loading-md" />
        </div>

        <div v-else-if="myPastes.length" class="space-y-3">
          <PasteCard v-for="item in myPastes" :key="item.id" :item="item" />
        </div>

        <p v-else class="opacity-75">در حال حاضر پیستی برای شما ثبت نشده است.</p>
      </div>
    </div>
  </section>
</template>
