<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { fa } from '@/utils/strings'
import { useAuthStore } from '@/stores/auth'
import logoSrc from '@/assets/logo-navbar.png'

const route = useRoute()
const authStore = useAuthStore()

const isAuthed = computed(() => authStore.isAuthenticated)

function logout() {
  authStore.logout()
}
</script>

<template>
  <header class="navbar surface sticky top-0 z-20 min-h-24 border-b px-3 md:min-h-28 md:px-6">
    <div class="navbar-start">
      <RouterLink to="/" class="rounded-2xl p-2 transition hover:bg-base-200/60 focus-ring">
        <img
          :src="logoSrc"
          alt="لوگو CopyFi"
          class="h-16 w-auto md:h-24 lg:h-28 rounded-2xl object-contain drop-shadow-sm"
        />
      </RouterLink>
    </div>

    <div class="navbar-center hidden md:flex">
      <ul class="menu menu-horizontal rounded-box bg-base-100/60 px-2">
        <li><RouterLink to="/" :class="{ active: route.path === '/' }">{{ fa.nav.home }}</RouterLink></li>
        <li><RouterLink to="/recent" :class="{ active: route.path.startsWith('/recent') }">{{ fa.nav.recent }}</RouterLink></li>
        <li v-if="isAuthed"><RouterLink to="/profile">{{ fa.nav.profile }}</RouterLink></li>
        <li v-if="isAuthed && authStore.user?.role === 'admin'"><RouterLink to="/admin/reports">{{ fa.nav.adminReports }}</RouterLink></li>
      </ul>
    </div>

    <div class="navbar-end gap-2 md:gap-3">
      <button class="btn btn-ghost btn-sm" disabled>{{ fa.common.language }}: فارسی</button>
      <RouterLink v-if="!isAuthed" to="/login" class="btn btn-outline btn-sm focus-ring">{{ fa.nav.login }}</RouterLink>
      <RouterLink v-if="!isAuthed" to="/register" class="btn btn-primary btn-sm focus-ring">{{ fa.nav.register }}</RouterLink>
      <button v-if="isAuthed" class="btn btn-error btn-sm focus-ring" @click="logout">{{ fa.common.logout }}</button>
    </div>
  </header>
</template>
