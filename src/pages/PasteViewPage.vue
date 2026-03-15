<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { fa } from '@/utils/strings'
import { formatFaDate } from '@/utils/formatters'
import { getPasteByIdRequest, getPasteRawRequest, reportPasteRequest } from '@/services/api/pastes'
import AlertMessage from '@/components/AlertMessage.vue'
import CodeViewer from '@/components/CodeViewer.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

const route = useRoute()

const loading = ref(false)
const error = ref('')
const paste = ref(null)
const notFound = ref(false)
const unlockPassword = ref('')
const needsPassword = ref(false)
const copied = ref(false)
const shared = ref(false)
const showReportModal = ref(false)
const reportSent = ref(false)

const isLocked = computed(() => needsPassword.value)

function normalizePaste(data) {
  return {
    id: data.id,
    slug: data.slug,
    title: data.title,
    content: data.content,
    language: data.language || 'plaintext',
    created_at: data.created_at,
    expire_at: data.expires_at,
    visibility: data.visibility,
    locked: false
  }
}

async function fetchPaste(password = null) {
  loading.value = true
  error.value = ''
  notFound.value = false

  try {
    const data = await getPasteByIdRequest(route.params.id, password)
    paste.value = normalizePaste(data)
    needsPassword.value = false
  } catch (err) {
    const status = err?.response?.status
    const apiError = err?.response?.data?.error

    if (status === 404) {
      notFound.value = true
    } else if (status === 401 && ['paste_password_required', 'invalid_paste_password'].includes(apiError?.code)) {
      needsPassword.value = true
      if (apiError?.code === 'invalid_paste_password') {
        error.value = 'رمز عبور نامعتبر است.'
      }
    } else {
      error.value = apiError?.message || 'خطا در دریافت پیست.'
    }
  } finally {
    loading.value = false
  }
}

async function unlockPaste() {
  if (!unlockPassword.value.trim()) {
    error.value = 'لطفا رمز عبور را وارد کنید.'
    return
  }

  await fetchPaste(unlockPassword.value.trim())
}

async function copyContent() {
  if (!paste.value?.content) return
  await navigator.clipboard.writeText(paste.value.content)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 1200)
}

async function sharePasteLink() {
  const url = `${window.location.origin}/p/${route.params.id}`
  try {
    if (navigator.share) {
      await navigator.share({
        title: paste.value?.title || 'Paste',
        url
      })
    } else {
      await navigator.clipboard.writeText(url)
    }
    shared.value = true
    setTimeout(() => {
      shared.value = false
    }, 1400)
  } catch (err) {
    if (err?.name === 'AbortError') return
    error.value = 'امکان اشتراک‌گذاری لینک وجود ندارد.'
  }
}

async function openRaw() {
  try {
    const rawText = await getPasteRawRequest(route.params.id, unlockPassword.value.trim() || null)
    const rawWindow = window.open('', '_blank')
    if (!rawWindow) return
    rawWindow.document.write(`<pre>${String(rawText).replace(/</g, '&lt;')}</pre>`)
  } catch (err) {
    error.value = err?.response?.data?.error?.message || 'خطا در دریافت نسخه خام.'
  }
}

function downloadPaste() {
  if (!paste.value?.content) return
  const blob = new Blob([paste.value.content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `paste-${paste.value.slug || paste.value.id}.txt`
  link.click()
  URL.revokeObjectURL(url)
}

async function submitReport() {
  try {
    await reportPasteRequest(route.params.id, 'محتوای مشکوک یا نامناسب')
    reportSent.value = true
    setTimeout(() => {
      reportSent.value = false
    }, 2000)
  } catch (err) {
    error.value = err?.response?.data?.error?.message || 'ثبت گزارش با خطا مواجه شد.'
  }
}

onMounted(() => fetchPaste())
</script>

<template>
  <section class="space-y-5">
    <div v-if="loading" class="flex justify-center p-8">
      <span class="loading loading-spinner loading-lg" />
    </div>

    <AlertMessage v-else-if="error" :message="error" type="error" />

    <AlertMessage v-if="copied" type="success" message="متن پیست کپی شد." />
    <AlertMessage v-if="shared" type="success" message="لینک پیست آماده اشتراک‌گذاری شد." />
    <AlertMessage v-if="reportSent" type="success" message="گزارش شما ثبت شد." />

    <div v-if="notFound" class="card surface">
      <div class="card-body">
        <h2 class="card-title">{{ fa.paste.pasteNotFound }}</h2>
      </div>
    </div>

    <article v-else-if="paste || isLocked" class="card surface">
      <div class="card-body gap-5">
        <div v-if="paste" class="flex flex-wrap items-start justify-between gap-3">
          <h1 class="card-title text-xl md:text-2xl">{{ paste.title || 'بدون عنوان' }}</h1>
          <div class="flex flex-wrap gap-2">
            <span class="badge badge-outline">{{ paste.language }}</span>
            <span class="badge badge-primary badge-outline">{{ paste.visibility }}</span>
          </div>
        </div>

        <div v-if="paste" class="stats stats-vertical md:stats-horizontal border border-base-300 bg-base-200/70">
          <div class="stat">
            <div class="stat-title">{{ fa.paste.createdAt }}</div>
            <div class="stat-value text-base">{{ formatFaDate(paste.created_at) }}</div>
          </div>
          <div class="stat">
            <div class="stat-title">{{ fa.paste.expiresAt }}</div>
            <div class="stat-value text-base">{{ formatFaDate(paste.expire_at) }}</div>
          </div>
          <div class="stat">
            <div class="stat-title">{{ fa.paste.visibilityLabel }}</div>
            <div class="stat-value text-base">{{ paste.visibility }}</div>
          </div>
        </div>

        <div v-if="isLocked" class="panel-soft space-y-3">
          <p>{{ fa.paste.privateLocked }}</p>
          <label class="form-control">
            <div class="label"><span class="label-text">{{ fa.paste.password }}</span></div>
            <input v-model="unlockPassword" type="password" class="input input-bordered focus-ring" />
          </label>
          <div>
            <button class="btn btn-primary" :disabled="loading" @click="unlockPaste">{{ fa.paste.unlockButton }}</button>
          </div>
        </div>

        <template v-else-if="paste">
          <CodeViewer :content="paste.content" :language="paste.language" />

          <div class="flex flex-wrap items-center gap-2 justify-start">
            <button class="btn btn-outline" @click="copyContent">{{ fa.paste.copy }}</button>
            <button class="btn btn-outline" @click="sharePasteLink">{{ fa.paste.share }}</button>
            <button class="btn btn-outline" @click="openRaw">{{ fa.paste.raw }}</button>
            <button class="btn btn-outline" @click="downloadPaste">{{ fa.paste.download }}</button>
            <button class="btn btn-warning" @click="showReportModal = true">{{ fa.paste.report }}</button>
          </div>
        </template>
      </div>
    </article>

    <ConfirmModal
      v-model="showReportModal"
      title="گزارش پیست"
      description="آیا از ارسال گزارش این پیست مطمئن هستید؟"
      confirm-text="ارسال گزارش"
      cancel-text="انصراف"
      @confirm="submitReport"
    />
  </section>
</template>
