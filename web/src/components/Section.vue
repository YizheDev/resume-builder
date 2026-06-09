<template>
  <div class="mb-6">
    <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">{{ title }}</h3>
    <slot />
  </div>
</template>

<script setup>
defineProps({ title: String })
</script>
