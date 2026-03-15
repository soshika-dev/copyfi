<script setup>
import AppNavbar from '@/components/AppNavbar.vue'
import AppToast from '@/components/AppToast.vue'
import Footer from '@/components/Footer.vue'
</script>

<template>
  <div class="app-shell flex min-h-screen flex-col">
    <div class="app-content">
      <AppToast />
      <AppNavbar />
      <main class="container mx-auto w-full max-w-5xl flex-1 p-3 md:p-6">
        <RouterView />
      </main>
      <Footer />
    </div>
  </div>
</template>
