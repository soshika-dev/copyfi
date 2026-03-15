<script setup>
import { computed, ref } from 'vue'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()
const linkCopied = ref(false)

const toastClass = computed(() => {
  if (!uiStore.toast) return 'alert-info'
  if (uiStore.toast.type === 'success') return 'alert-success'
  if (uiStore.toast.type === 'error') return 'alert-error'
  if (uiStore.toast.type === 'warning') return 'alert-warning'
  return 'alert-info'
})

const hasLink = computed(() => Boolean(uiStore.toast?.link))

async function copyLink() {
  if (!uiStore.toast?.link) return
  await navigator.clipboard.writeText(uiStore.toast.link)
  linkCopied.value = true
  setTimeout(() => {
    linkCopied.value = false
  }, 1200)
}
</script>

<template>
  <div v-if="uiStore.toast && hasLink" class="fixed inset-0 z-[90] flex items-center justify-center p-4 pointer-events-none">
    <div class="pointer-events-auto w-full max-w-xl rounded-2xl border border-sky-300/60 bg-white/95 p-4 shadow-2xl shadow-slate-900/15 backdrop-blur-md">
      <div class="mb-2 text-sm font-semibold text-slate-800">{{ uiStore.toast.message }}</div>

      <div class="rounded-xl border border-slate-200 bg-slate-50 p-3">
        <p class="mb-2 text-xs text-slate-500">{{ uiStore.toast.linkLabel }}</p>
        <div class="flex flex-wrap items-center gap-2">
          <a :href="uiStore.toast.link" class="flex-1 text-sm font-medium text-slate-800 underline" dir="ltr">
            {{ uiStore.toast.link }}
          </a>
          <button class="btn btn-sm border-0 bg-slate-900 text-white hover:bg-slate-800" @click="copyLink">
            {{ linkCopied ? 'کپی شد' : 'کپی لینک' }}
          </button>
        </div>
      </div>

      <div class="mt-3 flex justify-end">
        <button class="btn btn-ghost btn-sm" @click="uiStore.hideToast">بستن</button>
      </div>
    </div>
  </div>

  <div v-else-if="uiStore.toast" class="toast toast-top toast-start z-[80]">
    <div class="alert max-w-md shadow-lg" :class="toastClass">
      <div class="flex flex-col gap-1">
        <span>{{ uiStore.toast.message }}</span>
      </div>
      <button class="btn btn-ghost btn-xs" @click="uiStore.hideToast">✕</button>
    </div>
  </div>
</template>
