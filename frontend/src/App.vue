<template>
  <div class="shell">
    <header class="topbar">
      <RouterLink to="/" class="brand">Siblings Meetup Scheduler</RouterLink>
    </header>
    <main class="main">
      <RouterView />
    </main>
    <ToastBar />
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import ToastBar from './components/ToastBar.vue'
</script>
