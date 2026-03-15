<script setup>
import { RouterLink } from 'vue-router'
import { formatFaDate, toSnippet } from '@/utils/formatters'
import { fa } from '@/utils/strings'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <article class="card surface transition hover:-translate-y-0.5 hover:shadow-lg">
    <div class="card-body gap-3">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h3 class="card-title text-base md:text-lg">
          <RouterLink :to="`/p/${props.item.id}`" class="link link-hover">
            {{ props.item.title || 'بدون عنوان' }}
          </RouterLink>
        </h3>
        <div class="flex flex-wrap gap-2">
          <span class="badge badge-outline">{{ props.item.language || 'plaintext' }}</span>
          <span class="badge badge-ghost">{{ props.item.visibility || 'public' }}</span>
        </div>
      </div>

      <div class="text-sm opacity-80">
        <span>{{ fa.paste.createdAt }}: {{ formatFaDate(props.item.created_at) }}</span>
      </div>

      <p class="text-sm leading-8">{{ toSnippet(props.item.content || '') }}</p>
    </div>
  </article>
</template>
