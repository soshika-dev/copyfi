<script setup>
import { ref } from 'vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import AlertMessage from '@/components/AlertMessage.vue'

const reports = ref([
  { id: 1, paste_id: 'abc123', reason: 'محتوای نامناسب', created_at: '2026-01-30T08:00:00Z' },
  { id: 2, paste_id: 'def456', reason: 'اسپم', created_at: '2026-02-02T11:30:00Z' }
])

const selectedReportId = ref(null)
const modalOpen = ref(false)
const success = ref('')

function openDeleteModal(id) {
  selectedReportId.value = id
  modalOpen.value = true
}

function deleteReportPaste() {
  reports.value = reports.value.filter((item) => item.id !== selectedReportId.value)
  success.value = 'گزارش حذف شد (فقط UI).'
  setTimeout(() => {
    success.value = ''
  }, 1800)
}
</script>

<template>
  <section class="space-y-4">
    <h1 class="text-xl font-bold">مدیریت گزارش‌ها</h1>
    <AlertMessage v-if="success" type="success" :message="success" />

    <div class="overflow-x-auto bg-base-100 border border-base-300 rounded-xl">
      <table class="table">
        <thead>
          <tr>
            <th>شناسه گزارش</th>
            <th>شناسه پیست</th>
            <th>دلیل</th>
            <th>عملیات</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="report in reports" :key="report.id">
            <td>{{ report.id }}</td>
            <td>{{ report.paste_id }}</td>
            <td>{{ report.reason }}</td>
            <td>
              <button class="btn btn-error btn-sm" @click="openDeleteModal(report.id)">حذف پیست</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmModal
      v-model="modalOpen"
      title="حذف پیست"
      description="این عملیات فقط نمایشی است. ادامه می‌دهید؟"
      confirm-text="حذف"
      cancel-text="انصراف"
      @confirm="deleteReportPaste"
    />
  </section>
</template>
