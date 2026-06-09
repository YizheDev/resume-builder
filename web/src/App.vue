<template>
  <div class="min-h-screen bg-white font-sans text-gray-900 antialiased">
    <nav class="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <router-link to="/" class="flex items-center gap-2 text-xl font-bold text-brand-600">
          <span class="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white text-sm">R</span>
          Resume Builder
        </router-link>
        <div class="flex items-center gap-4 text-sm text-gray-500">
          <a href="#" class="hover:text-brand-600 transition">简历模板</a>
          <a href="#" class="hover:text-brand-600 transition">AI 生成</a>
          <a href="#" class="hover:text-brand-600 transition">使用帮助</a>
        </div>
      </div>
    </nav>
    <router-view />
    <footer class="bg-gray-50 border-t border-gray-100 py-12 mt-20">
      <div class="max-w-7xl mx-auto px-4 text-center text-sm text-gray-400">
        <p>Powered by AI · 让每个人都能拥有专业简历</p>
      </div>
    </footer>
  </div>
</template>
