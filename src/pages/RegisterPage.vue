<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AlertMessage from '@/components/AlertMessage.vue'
import { fa } from '@/utils/strings'
import logoSrc from '@/assets/logo-navbar.png'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: ''
})
const error = ref('')

async function submitRegister() {
  error.value = ''
  try {
    await authStore.register({ ...form.value })
    router.push('/')
  } catch (err) {
    error.value = err?.response?.data?.error?.message || 'ثبت‌نام ناموفق بود.'
  }
}
</script>

<template>
  <section class="mx-auto max-w-5xl">
    <div class="overflow-hidden rounded-3xl border border-slate-200/80 bg-white/80 shadow-2xl shadow-slate-900/10 backdrop-blur-xl">
      <div class="grid grid-cols-1 md:grid-cols-2">
        <aside class="order-2 md:order-1 border-t md:border-t-0 md:border-l border-slate-200/80 bg-slate-50/70 p-7 md:p-10">
          <div class="flex flex-col gap-6">
            <img :src="logoSrc" alt="لوگو CopyFi" class="h-20 w-auto md:h-24 rounded-2xl bg-white p-2 ring-1 ring-slate-200 object-contain" />
            <div>
              <h2 class="text-3xl font-bold tracking-tight text-slate-900">{{ fa.appName }}</h2>
              <p class="mt-3 text-sm leading-8 text-slate-600">
                حساب جدید بسازید و تمام پیست‌های عمومی و خصوصی خود را از یک پنل ساده مدیریت کنید.
              </p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-white/90 p-4">
              <p class="text-sm leading-7 text-slate-600">
                ثبت‌نام سریع، دسترسی امن و تجربه کاربری یکپارچه برای تیم‌های توسعه.
              </p>
            </div>
          </div>
        </aside>

        <form class="order-1 md:order-2 p-7 md:p-10" @submit.prevent="submitRegister">
          <div class="mb-8">
            <h1 class="text-3xl font-bold text-slate-900">{{ fa.auth.registerTitle }}</h1>
            <p class="mt-2 text-sm text-slate-500">برای شروع، اطلاعات حساب جدید را وارد کنید.</p>
          </div>

          <AlertMessage v-if="error" class="mb-4" :message="error" type="error" />

          <div class="space-y-4">
            <label class="form-control">
              <div class="label pb-1"><span class="label-text font-medium text-slate-700">{{ fa.auth.username }}</span></div>
              <input v-model="form.username" type="text" class="input input-bordered h-12 bg-white focus-ring" required />
            </label>

            <label class="form-control">
              <div class="label pb-1"><span class="label-text font-medium text-slate-700">{{ fa.auth.email }}</span></div>
              <input v-model="form.email" type="email" class="input input-bordered h-12 bg-white focus-ring" required />
            </label>

            <label class="form-control">
              <div class="label pb-1"><span class="label-text font-medium text-slate-700">{{ fa.auth.password }}</span></div>
              <input v-model="form.password" type="password" class="input input-bordered h-12 bg-white focus-ring" required />
            </label>
          </div>

          <button class="btn mt-7 h-12 w-full border-0 bg-slate-900 text-white hover:bg-slate-800" :disabled="authStore.loading">
            <span v-if="authStore.loading" class="loading loading-spinner loading-sm" />
            {{ fa.auth.register }}
          </button>

          <p class="mt-4 text-sm text-slate-600">
            {{ fa.auth.hasAccount }}
            <RouterLink class="link font-medium text-slate-900" to="/login">{{ fa.auth.login }}</RouterLink>
          </p>
        </form>
      </div>
    </div>
  </section>
</template>
