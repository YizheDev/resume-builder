<template>
  <div class="flex h-[calc(100vh-64px)]">
    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col max-w-3xl mx-auto bg-white">
      <!-- Progress Bar -->
      <div class="px-6 py-4 bg-white border-b sticky top-0 z-10">
        <div class="flex items-center justify-between mb-2">
          <span class="font-semibold text-brand-700">{{ resumeTitle }}</span>
          <span class="text-xs text-gray-400">{{ progress }}%</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-2">
          <div class="bg-brand-500 h-2 rounded-full transition-all duration-500" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <!-- Messages -->
      <div ref="chatRef" class="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        <!-- AI Message -->
        <div class="flex gap-3 items-start">
          <div class="w-10 h-10 bg-brand-600 rounded-xl flex items-center justify-center text-white text-sm shrink-0 shadow-sm">AI</div>
          <div class="bg-gray-50 border border-gray-100 rounded-2xl rounded-tl-none px-5 py-4 max-w-xl">
            <p class="text-sm leading-relaxed text-gray-700">{{ aiMessage }}</p>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="flex gap-2 ml-13 items-center text-gray-400 text-sm">
          <span class="animate-spin">⏳</span> AI 正在生成选项...
        </div>

        <!-- Personal Form -->
        <div v-if="currentModule === 'personal' && status === 'chatting' && !loading" class="ml-13 space-y-3">
          <div class="bg-white border border-gray-100 rounded-2xl p-5 space-y-3 shadow-sm">
            <div class="grid grid-cols-2 gap-3">
              <input v-model="personalForm.name" placeholder="姓名" class="p-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-brand-500" />
              <input v-model="personalForm.phone" placeholder="电话" class="p-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-brand-500" />
              <input v-model="personalForm.email" placeholder="邮箱" class="p-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-brand-500" />
              <input v-model="personalForm.city" placeholder="城市" class="p-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-brand-500" />
            </div>
            <div class="flex gap-2 pt-2">
              <button @click="submitPersonal" class="px-5 py-2.5 bg-brand-600 text-white rounded-xl text-sm font-medium hover:bg-brand-700 shadow-sm transition disabled:opacity-50" :disabled="loading">✅ 确认，继续</button>
              <button @click="skipModule" class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-500 hover:bg-gray-50 transition">⏭️ 跳过</button>
            </div>
          </div>
        </div>

        <!-- Options Area -->
        <div v-if="currentOptions && currentModule !== 'personal' && status === 'chatting' && !loading" class="ml-13 space-y-3">
          <!-- Skills -->
          <template v-if="currentModule === 'skills' && typeof currentOptions === 'object' && !Array.isArray(currentOptions)">
            <div class="space-y-4">
              <div v-if="currentOptions.must">
                <p class="text-xs font-semibold text-red-500 uppercase mb-2">🔴 必备</p>
                <div class="space-y-1">
                  <label v-for="o in currentOptions.must" :key="o.id" class="flex items-center gap-3 p-3 bg-white border border-gray-100 rounded-xl hover:border-brand-300 cursor-pointer transition">
                    <input type="checkbox" :value="o.label" v-model="selectedItems" class="w-4 h-4 accent-brand-600 rounded" />
                    <span class="text-sm">{{ o.label }}</span>
                  </label>
                </div>
              </div>
              <div v-if="currentOptions.plus">
                <p class="text-xs font-semibold text-yellow-600 uppercase mb-2">🟡 加分</p>
                <div class="space-y-1">
                  <label v-for="o in currentOptions.plus" :key="o.id" class="flex items-center gap-3 p-3 bg-white border border-gray-100 rounded-xl hover:border-brand-300 cursor-pointer transition">
                    <input type="checkbox" :value="o.label" v-model="selectedItems" class="w-4 h-4 accent-brand-600 rounded" />
                    <span class="text-sm">{{ o.label }}</span>
                  </label>
                </div>
              </div>
            </div>
          </template>
          <!-- Summary -->
          <template v-else-if="currentModule === 'summary' && Array.isArray(currentOptions)">
            <div class="space-y-3">
              <div v-for="o in currentOptions" :key="o.id" @click="selectSummary(o)" class="p-4 bg-white border-2 border-gray-100 rounded-xl hover:border-brand-400 cursor-pointer transition hover:shadow-sm">
                <p class="text-xs text-brand-500 font-medium mb-1.5">{{ o.style }}</p>
                <p class="text-sm text-gray-700 leading-relaxed">{{ o.label }}</p>
              </div>
            </div>
          </template>
          <!-- Other modules -->
          <template v-else>
            <div class="space-y-1">
              <label v-for="o in currentOptions" :key="o.id" class="flex items-center gap-3 p-3 bg-white border border-gray-100 rounded-xl hover:border-brand-300 cursor-pointer transition">
                <input type="checkbox" :value="o.label" v-model="selectedItems" class="w-4 h-4 accent-brand-600 rounded" />
                <span class="text-sm text-gray-700">{{ o.label }}</span>
              </label>
            </div>
          </template>

          <!-- Custom Input -->
          <div class="pt-3 border-t border-gray-100">
            <textarea v-model="customInput" rows="2" class="w-full p-3 border border-gray-200 rounded-xl text-sm resize-none focus:ring-2 focus:ring-brand-500" placeholder="✏️ 其他补充（AI 自动润色）..."></textarea>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-2">
            <button @click="submitSelections" :disabled="loading" class="px-5 py-2.5 bg-brand-600 text-white rounded-xl text-sm font-medium hover:bg-brand-700 shadow-sm transition disabled:opacity-50">✅ 确认</button>
            <button @click="skipModule" class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-500 hover:bg-gray-50 transition">⏭️ 跳过</button>
            <button v-if="currentModule === 'summary'" @click="regenerateSummary" :disabled="loading" class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-500 hover:bg-gray-50 transition">🔄 换一批</button>
          </div>
        </div>

        <!-- Done State -->
        <div v-if="status === 'draft'" class="text-center py-16">
          <div class="text-5xl mb-4">🎉</div>
          <h2 class="text-2xl font-bold mb-2">简历生成完成！</h2>
          <p class="text-gray-500 mb-6">AI 已为你生成完整简历</p>
          <div class="flex gap-3 justify-center">
            <router-link :to="`/edit/${resumeId}`" class="px-8 py-3.5 bg-brand-600 text-white rounded-xl font-semibold text-lg hover:bg-brand-700 shadow-lg shadow-brand-200 transition">
              ✏️ 编辑完善 →
            </router-link>
            <a :href="`/api/resumes/${resumeId}/export?format=pdf`" target="_blank" class="px-8 py-3.5 bg-green-600 text-white rounded-xl font-semibold text-lg hover:bg-green-700 shadow-lg shadow-green-200 transition">
              📄 导出 PDF
            </a>
          </div>
        </div>
      </div>

      <!-- JD Input -->
      <div v-if="status !== 'draft'" class="px-6 py-4 bg-gray-50 border-t flex gap-2">
        <input v-model="jdText" placeholder="🎯 粘贴职位 JD（AI 自动匹配关键词）" class="flex-1 px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500" />
        <button @click="optimizeJD" :disabled="loading" class="px-5 py-2.5 bg-purple-600 text-white rounded-xl text-sm font-medium hover:bg-purple-700 transition disabled:opacity-50 whitespace-nowrap">优化</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const resumeId = route.params.id
const resumeTitle = ref('')
const aiMessage = ref('正在分析...')
const currentModule = ref('')
const currentOptions = ref(null)
const selectedItems = ref([])
const customInput = ref('')
const personalForm = reactive({ name: '', phone: '', email: '', city: '' })
const status = ref('chatting')
const progress = ref(0)
const loading = ref(false)
const jdText = ref('')
const chatRef = ref(null)

onMounted(async () => {
  const res = await fetch(`/api/resumes/${resumeId}`)
  const d = await res.json()
  resumeTitle.value = d.data?.title || ''
  await loadNext()
})

const loadNext = async () => {
  loading.value = true
  try {
    const res = await fetch(`/api/resumes/${resumeId}/chat`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'next' }),
    })
    if (!res.ok) throw new Error('API ' + res.status)
    const d = await res.json()
    const data = d.data
    aiMessage.value = data.reply
    currentModule.value = data.module
    currentOptions.value = data.options
    status.value = data.status || 'chatting'
    if (data.module === 'done' || data.status === 'ready') {
      progress.value = 100
      status.value = 'draft'
      autoGenerate()
    } else {
      progress.value = Math.min(90, Math.round(progress.value + 14))
    }
    selectedItems.value = []
    customInput.value = ''
    await nextTick()
    chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })
  } catch(e) {
    console.error('loadNext failed:', e)
    aiMessage.value = '网络异常，请刷新页面重试'
  } finally {
    loading.value = false
  }
}

const autoGenerate = async () => {
  try {
    await fetch('/api/resumes/' + resumeId + '/generate', { method: 'POST' })
  } catch(e) { console.error('autoGenerate failed:', e) }
}

const submitPersonal = async () => {
  loading.value = true
  await fetch(`/api/resumes/${resumeId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: { personal: { ...personalForm } } }),
  })
  loading.value = false
  loadNext()
}

const submitSelections = async () => {
  if (!currentModule.value) return
  loading.value = true
  await fetch(`/api/resumes/${resumeId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selections: { [currentModule.value]: selectedItems.value },
      data: { [currentModule.value]: { selected: selectedItems.value, custom: customInput.value } },
    }),
  })
  loading.value = false
  loadNext()
}

const skipModule = () => { selectedItems.value = []; customInput.value = ''; submitSelections() }
const selectSummary = async (o) => {
  loading.value = true
  await fetch(`/api/resumes/${resumeId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: { summary: o.label } }),
  })
  loading.value = false
  submitSelections()
}
const regenerateSummary = () => loadNext()
const optimizeJD = async () => {
  if (!jdText.value.trim()) return
  loading.value = true
  await fetch(`/api/resumes/${resumeId}/jd-optimize`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jd: jdText.value }) })
  jdText.value = ''
  aiMessage.value = 'JD 已分析！继续下一步吧。'
  loading.value = false
}
</script>

<style scoped>
.ml-13 { margin-left: 52px; }
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; display: inline-block; }
</style>
