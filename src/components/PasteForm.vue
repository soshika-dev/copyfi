<script setup>
import { computed, ref } from 'vue'
import { fa, languages } from '@/utils/strings'
import AlertMessage from '@/components/AlertMessage.vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit'])

const form = ref({
  title: '',
  content: '',
  language: 'plaintext',
  expire_at: 'never',
  visibility: 'public',
  password: ''
})

const fileInputRef = ref(null)
const selectedFile = ref(null)
const readingFile = ref(false)
const error = ref('')
const needPassword = computed(() => form.value.visibility === 'private')
const maxFileSize = 2 * 1024 * 1024

const languageByExtension = {
  txt: 'plaintext',
  js: 'javascript',
  ts: 'javascript',
  py: 'python',
  html: 'html',
  htm: 'html',
  css: 'css',
  json: 'json',
  md: 'plaintext',
  log: 'plaintext',
  vue: 'html'
}

function prettyFileSize(size) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

async function handleFileChange(event) {
  error.value = ''
  const file = event.target.files?.[0]
  if (!file) return

  if (file.size > maxFileSize) {
    error.value = 'حجم فایل باید کمتر از ۲ مگابایت باشد.'
    if (fileInputRef.value) fileInputRef.value.value = ''
    return
  }

  readingFile.value = true
  try {
    const text = await file.text()

    if (!text.trim()) {
      error.value = 'فایل انتخاب‌شده خالی است.'
      return
    }

    form.value.content = text
    if (!form.value.title.trim()) {
      form.value.title = file.name
    }

    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext && languageByExtension[ext]) {
      form.value.language = languageByExtension[ext]
    }

    selectedFile.value = {
      name: file.name,
      size: file.size
    }
  } catch {
    error.value = 'خواندن فایل با خطا مواجه شد.'
  } finally {
    readingFile.value = false
  }
}

function removeFile() {
  selectedFile.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

function handleSubmit() {
  error.value = ''

  if (!form.value.content.trim()) {
    error.value = fa.paste.emptyError
    return
  }

  const payload = {
    title: form.value.title.trim(),
    content: form.value.content,
    language: form.value.language,
    expire_at: form.value.expire_at,
    visibility: form.value.visibility
  }

  if (needPassword.value && form.value.password.trim()) {
    payload.password = form.value.password.trim()
  }

  emit('submit', payload)
}
</script>

<template>
  <form class="card overflow-hidden border border-slate-200/80 bg-white/80 shadow-xl shadow-slate-900/5 backdrop-blur-xl" @submit.prevent="handleSubmit">
    <div class="h-1.5 w-full bg-gradient-to-r from-slate-800 via-sky-600 to-cyan-500"></div>
    <div class="card-body gap-6 p-5 md:p-7">
      <header class="space-y-2 text-right">
        <h2 class="card-title text-2xl text-slate-900">{{ fa.paste.createTitle }}</h2>
        <p class="text-sm text-slate-500">متن خود را وارد کنید، تنظیمات را انتخاب کنید و پیست را ایجاد کنید.</p>
      </header>

      <AlertMessage v-if="error" :message="error" type="error" />

      <section class="space-y-4 rounded-2xl border border-slate-200 bg-white p-4 md:p-5">
        <label class="form-control w-full">
          <div class="label">
            <span class="label-text font-medium text-slate-700">{{ fa.paste.title }}</span>
          </div>
          <input v-model="form.title" type="text" class="input input-bordered w-full bg-slate-50 focus-ring" />
        </label>

        <label class="form-control w-full">
          <div class="label">
            <span class="label-text font-medium text-slate-700">{{ fa.paste.content }}</span>
          </div>
          <textarea
            v-model="form.content"
            class="textarea textarea-bordered min-h-80 w-full bg-slate-50 focus-ring"
            required
            aria-required="true"
          />
        </label>

        <div class="rounded-xl border border-slate-200/80 bg-slate-50 p-3">
          <div class="mb-2 flex items-center justify-between gap-2">
            <span class="text-sm font-medium text-slate-700">{{ fa.paste.attachFile }}</span>
            <span class="text-xs text-slate-500">حداکثر: ۲MB</span>
          </div>

          <input
            ref="fileInputRef"
            type="file"
            class="file-input file-input-bordered w-full bg-white focus-ring"
            accept=".txt,.js,.ts,.py,.html,.htm,.css,.json,.md,.log,.vue,text/plain,text/*"
            @change="handleFileChange"
          />

          <p v-if="readingFile" class="mt-2 text-xs text-slate-500">در حال خواندن فایل...</p>

          <div v-else-if="selectedFile" class="mt-2 flex flex-wrap items-center gap-2">
            <span class="badge badge-outline">{{ selectedFile.name }}</span>
            <span class="text-xs text-slate-500">{{ prettyFileSize(selectedFile.size) }}</span>
            <button type="button" class="btn btn-ghost btn-xs" @click="removeFile">{{ fa.paste.removeFile }}</button>
          </div>

          <p class="mt-2 text-xs text-slate-500">{{ fa.paste.attachHelp }}</p>
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-slate-50/70 p-4 md:p-5">
        <div class="mb-3 text-sm font-medium text-slate-600">تنظیمات پیست</div>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <label class="form-control">
          <div class="label">
              <span class="label-text font-medium text-slate-700">{{ fa.paste.language }}</span>
          </div>
            <select v-model="form.language" class="select select-bordered w-full bg-white focus-ring">
            <option v-for="lang in languages" :key="lang" :value="lang">{{ lang }}</option>
          </select>
        </label>

          <label class="form-control">
          <div class="label">
              <span class="label-text font-medium text-slate-700">{{ fa.paste.expire }}</span>
          </div>
            <select v-model="form.expire_at" class="select select-bordered w-full bg-white focus-ring">
            <option value="never">{{ fa.expirationOptions.never }}</option>
            <option value="10m">{{ fa.expirationOptions.m10 }}</option>
            <option value="1h">{{ fa.expirationOptions.h1 }}</option>
            <option value="1d">{{ fa.expirationOptions.d1 }}</option>
            <option value="1w">{{ fa.expirationOptions.w1 }}</option>
          </select>
        </label>

          <label class="form-control">
          <div class="label">
              <span class="label-text font-medium text-slate-700">{{ fa.paste.visibility }}</span>
          </div>
            <select v-model="form.visibility" class="select select-bordered w-full bg-white focus-ring">
            <option value="public">{{ fa.visibilityOptions.public }}</option>
            <option value="unlisted">{{ fa.visibilityOptions.unlisted }}</option>
            <option value="private">{{ fa.visibilityOptions.private }}</option>
          </select>
        </label>
        </div>
      </section>

      <label v-if="needPassword" class="form-control rounded-2xl border border-slate-200 bg-slate-50/70 p-4 md:p-5">
        <div class="label">
          <span class="label-text font-medium text-slate-700">{{ fa.paste.password }}</span>
        </div>
        <input v-model="form.password" type="password" class="input input-bordered w-full bg-white focus-ring" />
      </label>

      <div class="card-actions justify-start">
        <button
          class="btn min-w-40 border-0 bg-slate-900 text-white hover:bg-slate-800"
          :class="{ 'btn-disabled': loading }"
          type="submit"
          :disabled="loading"
        >
          <span v-if="loading" class="loading loading-spinner loading-sm" />
          {{ fa.paste.create }}
        </button>
      </div>
    </div>
  </form>
</template>
