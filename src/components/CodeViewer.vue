<script setup>
defineProps({
  content: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'plaintext'
  }
})
</script>

<template>
  <div class="rounded-2xl border border-base-300 bg-base-100/90 p-1">
    <div class="mockup-code max-h-[520px] overflow-auto rounded-xl" dir="ltr">
      <pre class="text-left"><code>{{ content }}</code></pre>
    </div>
  </div>
  <p class="mt-2 text-xs opacity-70">زبان: {{ language }}</p>
</template>
