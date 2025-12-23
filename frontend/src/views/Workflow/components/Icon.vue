<script setup lang="ts">
defineProps({
  name: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <svg v-if="name === 'reset'" width="16" height="16" viewBox="0 0 32 32">
    <path d="M18 28A12 12 0 1 0 6 16v6.2l-3.6-3.6L1 20l6 6l6-6l-1.4-1.4L8 22.2V16a10 10 0 1 1 10 10Z" />
  </svg>

  <svg v-if="name === 'log'" width="16" height="16" viewBox="0 0 24 24">
    <path
      d="M20 19V7H4v12h16m0-16a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h16m-7 14v-2h5v2h-5m-3.42-4L5.57 9H8.4l3.3 3.3c.39.39.39 1.03 0 1.42L8.42 17H5.59l3.99-4Z" />
  </svg>
</template>