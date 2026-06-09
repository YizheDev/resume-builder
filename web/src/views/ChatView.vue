<template>
  <div class="flex h-screen">
    <!-- 左侧聊天区 -->
    <div class="w-3/5 flex flex-col border-r bg-white">
      <!-- 顶部进度条 -->
      <div class="px-6 py-3 border-b bg-gray-50">
        <div class="flex items-center justify-between text-sm">
          <span class="font-medium">{{ resumeTitle }}</span>
          <span class="text-gray-400">{{ currentModule }} / {{ totalModules }}</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-1.5 mt-2">
          <div class="bg-blue-600 h-1.5 rounded-full transition-all" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <!-- 对话区 -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
        <!-- AI 问候 -->
        <div class="flex gap-3">
          <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs">AI</div>
          <div class="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3 max-w-md">
            <p class="text-sm">{{ aiMessage }}</p>
          </div>
        </div>

        <!-- 选项列表 -->
        <div v-if="currentOptions" class="ml-11 space-y-2">
          <template v-if="currentModule === 'skills'">
            <div v-if="currentOptions.must" class="mb-3">
              <p class="text-xs font-medium text-red-500 mb-2">🔴 必备</p>
              <label v-for="o in currentOptions.must" :key="o.id" class="flex items-center gap-2 p-2 hover:bg-blue-50 rounded cursor-pointer">
                <input type="checkbox" :value="o.label" v-model="selectedItems" class="accent-blue-600" />
                <span class="text-sm">{{ o.label }}</span>
              </label>
            </div>
            <div v-if="currentOptions.plus" class="mb-3">
              <p class="text-xs font-medium text-yellow-500 mb-2">🟡 加分</p>
              <label v-for="o in currentOptions.plus" :key="o.id" class="flex items-center gap-2 p-2 hover:bg-blue-50 rounded cursor-pointer">
                <input type="checkbox" :value="o.label" v-model="selectedItems" class="accent-blue-600" />
                <span class="text-sm">{{ o.label }}</span>
              </label>
            </div>
          </template>
          <template v-else-if="currentModule === 'summary'">
            <div v-for="o in currentOptions" :key="o.id" @click="selectSummary(o)" class="p-3 border rounded-lg hover:border-blue-400 cursor-pointer transition">
              <p class="text-xs text-gray-400 mb-1">{{ o.style }}</p>
              <p class="text-sm">{{ o.label }}</p>
            </div>
          </template>
          <template v-else>
            <label v-for="o in currentOptions" :key="o.id" class="flex items-center gap-2 p-2 hover:bg-blue-50 rounded-lg cursor-pointer">
              <input type="checkbox" :value="o.label" v-model="selectedItems" class="accent-blue-600" />
              <span class="text-sm">{{ o.label }}</span>
            </label>
          </template>

          <!-- 自定义输入 -->
          <div class="mt-3 pt-3 border-t">
            <textarea v-model="customInput" rows="2" class="w-full p-2 border rounded-lg text-sm" placeholder="其他（自己补充，AI 自动润色）..."></textarea>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-2 mt-3">
            <button @click="submitSelections" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">✅ 确认</button>
            <button @click="skipModule" class="px-4 py-2 border rounded-lg text-sm text-gray-500 hover:bg-gray-50">⏭️ 跳过</button>
            <button v-if="currentModule === 'summary'" @click="regenerateSummary" class="px-4 py-2 border rounded-lg text-sm text-gray-500 hover:bg-gray-50">🔄 换一批</button>
          </div>
        </div>

        <!-- 完成状态 -->
        <div v-if="status === 'draft' || status === 'done'" class="text-center py-10">
          <p class="text-2xl mb-4">🎉 简历已生成！</p>
          <router-link :to="`/edit/${resumeId}`" class="inline-block px-6 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700">
            前往编辑 →
          </router-link>
        </div>
      </div>

      <!-- JD 输入 -->
      <div v-if="status !== 'draft'" class="px-6 py-3 border-t bg-gray-50 flex gap-2">
        <input v-model="jdText" placeholder="粘贴职位描述 JD（可选，AI 帮你优化关键词匹配）" class="flex-1 px-3 py-2 border rounded-lg text-xs" />
        <button @click="optimizeJD" class="px-4 py-2 bg-purple-600 text-white rounded-lg text-xs hover:bg-purple-700">🎯 优化</button>
      </div>
    </div>

    <!-- 右侧 A4 预览 -->
    <div class="w-2/5 bg-gray-200 p-6 overflow-y-auto">
      <div class="bg-white shadow-lg mx-auto" style="width:210mm; min-height:297mm; padding:20mm; transform:scale(0.6); transform-origin:top left;">
        <div v-if="previewData.personal?.name">
          <h1 style="font-size:24px;margin-bottom:4px">{{ previewData.personal.name || '姓名' }}</h1>
          <p style="font-size:12px;color:#666;margin-bottom:16px">{{ previewData.personal.phone }} · {{ previewData.personal.email }} · {{ previewData.personal.city }}</p>
          <div v-if="previewData.experience?.length" style="margin-bottom:12px">
            <h2 style="font-size:16px;color:#1a1a2e;border-bottom:1px solid #ddd;padding-bottom:4px">工作经历</h2>
            <div v-for="e in previewData.experience" :key="e.company" style="margin-bottom:8px">
              <strong>{{ e.title }}</strong> — {{ e.company }}<br>
              <span style="color:#666;font-size:12px">{{ e.start }} - {{ e.end }}</span>
              <ul style="margin:4px 0 0 16px;font-size:12px"><li v-for="h in e.highlights" :key="h">{{ h }}</li></ul>
            </div>
          </div>
          <div v-if="previewData.education?.length" style="margin-bottom:12px">
            <h2 style="font-size:16px;color:#1a1a2e;border-bottom:1px solid #ddd;padding-bottom:4px">教育背景</h2>
            <div v-for="e in previewData.education" :key="e.school"><strong>{{ e.school }}</strong> · {{ e.major }} · {{ e.degree }}</div>
          </div>
          <div v-if="previewData.skills?.length">
            <h2 style="font-size:16px;color:#1a1a2e;border-bottom:1px solid #ddd;padding-bottom:4px">技能</h2>
            <span v-for="s in previewData.skills" :key="s.name" style="display:inline-block;background:#f0f0f0;padding:2px 8px;margin:2px;border-radius:4px;font-size:11px">{{ s.name }} <span style="color:#999">{{ s.level }}</span></span>
          </div>
        </div>
        <div v-else class="text-center text-gray-300 py-20 text-sm">简历预览将在此显示</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const resumeId = route.params.id
const resumeTitle = ref('')
const aiMessage = ref('正在分析...')
const currentModule = ref('')
const currentOptions = ref(null)
const selectedItems = ref([])
const customInput = ref('')
const status = ref('chatting')
const progress = ref(0)
const jdText = ref('')
const previewData = reactive({ personal: {}, education: [], experience: [], skills: [], projects: [], awards: [], summary: '' })
const totalModules = 7
const modules = ['personal', 'education', 'awards', 'experience', 'projects', 'skills', 'summary']

const chatContainer = ref(null)

onMounted(async () => {
  const res = await fetch(`/api/resumes/${resumeId}`)
  const d = await res.json()
  resumeTitle.value = d.data?.title || ''
  await loadNextModule()
})

const loadNextModule = async () => {
  const res = await fetch(`/api/resumes/${resumeId}/chat`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'next' }),
  })
  const d = await res.json()
  const data = d.data
  aiMessage.value = data.reply
  currentModule.value = data.module
  currentOptions.value = data.options
  status.value = data.status || 'chatting'
  const idx = modules.indexOf(data.module)
  progress.value = Math.round(((idx >= 0 ? idx : 7) / totalModules) * 100)
  selectedItems.value = []
  customInput.value = ''
  await nextTick()
  chatContainer.value?.scrollTo({ top: chatContainer.value.scrollHeight, behavior: 'smooth' })
}

const submitSelections = async () => {
  // 保存选择
  await fetch(`/api/resumes/${resumeId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selections: { [currentModule.value]: selectedItems.value },
      data: { [currentModule.value]: { selected: selectedItems.value, custom: customInput.value } },
    }),
  })
  // 更新预览
  updatePreview()
  if (status.value === 'ready' || currentModule.value === 'done') {
    // 生成完整简历
    const res = await fetch(`/api/resumes/${resumeId}/generate`, { method: 'POST' })
    const d = await res.json()
    if (d.data?.content) {
      Object.assign(previewData, d.data.content)
    }
    status.value = 'draft'
    return
  }
  loadNextModule()
}

const skipModule = () => {
  selectedItems.value = []
  customInput.value = ''
  submitSelections()
}

const selectSummary = async (o) => {
  await fetch(`/api/resumes/${resumeId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: { summary: o.label } }),
  })
  previewData.summary = o.label
  submitSelections()
}

const regenerateSummary = async () => {
  const res = await fetch(`/api/resumes/${resumeId}/chat`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'regenerate', module: 'summary' }),
  })
  const d = await res.json()
  currentOptions.value = d.data?.options
}

const optimizeJD = async () => {
  if (!jdText.value.trim()) return
  await fetch(`/api/resumes/${resumeId}/jd-optimize`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jd: jdText.value }),
  })
  aiMessage.value = 'JD 已分析！关键词已应用到简历。继续下一步吧。'
  jdText.value = ''
}

const updatePreview = () => {
  previewData.personal = previewData.personal || {}
  previewData.education = previewData.education || []
  previewData.experience = previewData.experience || []
}
</script>
