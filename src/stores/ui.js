import { defineStore } from 'pinia'

let toastTimeout

export const useUiStore = defineStore('ui', {
  state: () => ({
    toast: null
  }),
  actions: {
    showToast(message, type = 'info', duration = 2600, options = {}) {
      this.toast = {
        id: Date.now(),
        message,
        type,
        link: options.link || '',
        linkLabel: options.linkLabel || 'مشاهده'
      }

      clearTimeout(toastTimeout)
      toastTimeout = setTimeout(() => {
        this.toast = null
      }, duration)
    },
    hideToast() {
      clearTimeout(toastTimeout)
      this.toast = null
    }
  }
})
