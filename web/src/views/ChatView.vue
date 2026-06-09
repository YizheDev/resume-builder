<template>
  <div class="flex h-[calc(100vh-64px)]">
    <!-- Left Chat -->
    <div class="w-3/5 flex flex-col bg-white border-r">
      <!-- Progress -->
      <div class="px-6 py-4 bg-white border-b">
        <div class="flex items-center justify-between mb-2">
          <span class="font-semibold text-brand-700">{{ resumeTitle }}</span>
          <span class="text-xs text-gray-400">{{ progress }}%</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-2">
          <div class="bg-brand-500 h-2 rounded-full transition-all duration-500" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <!-- Messages -->
      <div ref="chatRef" class="flex-1 overflow-y-auto px-6 py-6 space-y-6 bg-gradient-to-b from-gray-50 to-white">
        <div class="flex gap-3 items-start">
          <div class="w-10 h-10 bg-brand-600 rounded-xl flex items-center justify-center text-white text-sm shrink-0 shadow-sm">AI</div>
          <div class="bg-white border border-gray-100 rounded-2xl rounded-tl-none px-5 py-4 shadow-sm max-w-lg">
            <p class="text-sm leading-relaxed text-gray-700">{{ aiMessage }}</p>
          </div>
        </div>

        <!-- Person form -->
        <div v-if="currentModule === 'personal' && status === 'chatting'" class="ml-13 space-y-3">
          <div class="bg-white border border-gray-100 rounded-2xl p-5 space-y-3 shadow-sm">
            <div class="grid grid-cols-2 gap-3">
              <input v-model="personalForm.name" placeholder="姓名" class="p-2.5 border border-gray-200 rounded-lg text-sm" />
              <input v-model="personalForm.phone" placeholder="电话" class="p-2.5 border border-gray-200 rounded-lg text-sm" />
              <input v-model="personalForm.email" placeholder="邮箱" class="p-2.5 border border-gray-200 rounded-lg text-sm" />
              <input v-model="personalForm.city" placeholder="城市" class="p-2.5 border border-gray-200 rounded-lg text-sm" />
            </div>
            <div class="flex gap-2 pt-2">
              <button @click="submitPersonal" class="px-5 py-2.5 bg-brand-600 text-white rounded-xl text-sm font-medium hover:bg-brand-700 shadow-sm transition">✅ 确认，继续</button>
              <button @click="skipModule" class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-500 hover:bg-gray-50 transition">⏭️ 跳过</button>
            </div>
          </div>
        </div>

        <!-- Options -->
        <div v-if="currentOptions && currentModule !== 'personal' && status !== 'draft'" class="ml-13 space-y-3 pl-2">
          <template v-if="currentModule === 'skills' && typeof currentOptions === 'object' && !Array.isArray(currentOptions)">
            <div class="space-y-4">
              <div v-if="currentOptions.must">
                <p class="text-xs font-semibold text-red-500 uppercase tracking-wide mb-2">🔴 必备技能</p>
                <label v-for="o in currentOptions.must" :key="o.id" class="flex items-center gap-3 p-3 bg-white border border-gray-100 rounded-xl hover:border-brand-300 cursor-pointer transition">
                  <input type="checkbox" :value="o.label" v-model="selectedItems" class="w-4 h-4 accent-brand-600 rounded" />
                  <span class="text-sm">{{ o.label }}</span>
                </label>
              </div>
              <div v-if="currentOptions.plus">
                <p class="text-xs font-semibold text-yellow-600 uppercase tracking-wide mb-2">🟡 加分技能</p>
                <label v-for="o in currentOptions.plus" :key="o.id" class="flex items-center gap-3 p-3 bg-white border border-gray-100 rounded-xl hover:border-brand-300 cursor-pointer transition">
                  <input type="checkbox" :value="o.label" v-model="selectedItems" class="w-4 h-4 accent-brand-600 rounded" />
                  <span class="text-sm">{{ o.label }}</span>
                </label>
              </div>
            </div>
          </template>
          <template v-else-if="currentModule === 'summary' && Array.isArray(currentOptions)">
            <div class="space-y-3">
              <div v-for="o in currentOptions" :key="o.id" @click="selectSummary(o)" class="p-4 bg-white border-2 border-gray-100 rounded-xl hover:border-brand-400 cursor-pointer transition hover:shadow-sm">
                <p class="text-xs text-brand-500 font-medium mb-1.5">{{ o.style }}</p>
                <p class="text-sm text-gray-700 leading-relaxed">{{ o.label }}</p>
              </div>
            </div>
          </template>
          <template v-else-if="currentOptions">
            <div class="space-y-1">
              <label v-for="o in currentOptions" :key="o.id" class="flex items-center gap-3 p-3 hover:bg-brand-50 rounded-xl cursor-pointer transition">
                <input type="checkbox" :value="o.label" v-model="selectedItems" class="w-4 h-4 accent-brand-600 rounded" />
                <span class="text-sm text-gray-700">{{ o.label }}</span>
              </label>
            </div>
          </template>

          <!-- Custom input -->
          <div class="pt-3 border-t border-gray-100">
            <textarea v-model="customInput" rows="2" class="w-full p-3 border border-gray-200 rounded-xl text-sm resize-none focus:ring-2 focus:ring-brand-500 focus:border-transparent" placeholder="✏️ 其他补充（AI 自动润色为专业措辞）..."></textarea>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-2">
            <button @click="submitSelections" class="px-5 py-2.5 bg-brand-600 text-white rounded-xl text-sm font-medium hover:bg-brand-700 shadow-sm transition">✅ 确认</button>
            <button @click="skipModule" class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-500 hover:bg-gray-50 transition">⏭️ 跳过</button>
            <button v-if="currentModule === 'summary'" @click="regenerateSummary" class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-500 hover:bg-gray-50 transition">🔄 换一批</button>
          </div>
        </div>

        <!-- Done -->
        <div v-if="status === 'draft'" class="text-center py-16">
          <div class="text-5xl mb-4">🎉</div>
          <h2 class="text-2xl font-bold mb-2">简历生成完成！</h2>
          <p class="text-gray-500 mb-6">AI 已为你生成完整简历，可前往编辑页面微调</p>
          <router-link :to="`/edit/${resumeId}`" class="inline-block px-8 py-3.5 bg-brand-600 text-white rounded-xl font-semibold text-lg hover:bg-brand-700 shadow-lg shadow-brand-200 transition">
            前往编辑优化 →
          </router-link>
        </div>
      </div>

      <!-- JD input -->
      <div v-if="status !== 'draft'" class="px-6 py-4 bg-gray-50 border-t flex gap-2">
        <input v-model="jdText" placeholder="🎯 粘贴职位 JD（AI 自动匹配关键词加分）" class="flex-1 px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500" />
        <button @click="optimizeJD" class="px-5 py-2.5 bg-purple-600 text-white rounded-xl text-sm font-medium hover:bg-purple-700 transition whitespace-nowrap">优化</button>
      </div>
    </div>

    <!-- Right Preview -->
    <div class="w-2/5 bg-gray-100 p-6 overflow-y-auto flex items-start justify-center">
      <div class="bg-white shadow-2xl rounded-sm sticky top-6" style="width:210mm; min-height:297mm; padding:20mm; transform:scale(0.58); transform-origin:top center;">
        <div v-if="previewData.personal?.name" class="text-xs">
          <h1 style="font-size:20px;font-weight:700;margin-bottom:4px;color:#1a1a2e">{{ previewData.personal.name || '姓名' }}</h1>
          <p style="font-size:10px;color:#666;margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid #2563eb">
            {{ [previewData.personal.phone, previewData.personal.email, previewData.personal.city].filter(Boolean).join(' · ') }}
            <span v-if="previewData.personal.linkedin" class="ml-2">{{ previewData.personal.linkedin }}</span>
          </p>
          <div v-if="previewData.summary" style="margin-bottom:12px">
            <h2 style="font-size:13px;font-weight:700;color:#2563eb;margin-bottom:4px">自我评价</h2>
            <p style="font-size:10px;color:#444;line-height:1.6">{{ previewData.summary }}</p>
          </div>
          <div v-if="previewData.experience?.length" style="margin-bottom:12px">
            <h2 style="font-size:13px;font-weight:700;color:#2563eb;margin-bottom:4px">工作经历</h2>
            <div v-for="e in previewData.experience" :key="e.company" style="margin-bottom:8px">
              <div style="display:flex;justify-content:space-between"><strong style="font-size:11px">{{ e.title }}</strong><span style="font-size:9px;color:#888">{{ e.start }} - {{ e.end }}</span></div>
              <div style="font-size:10px;color:#555;margin-bottom:2px">{{ e.company }}</div>
              <ul style="margin:2px 0 0 14px;font-size:9px;color:#555;line-height:1.5"><li v-for="h in e.highlights" :key="h">{{ h }}</li></ul>
            </div>
          </div>
          <div v-if="previewData.projects?.length" style="margin-bottom:12px">
            <h2 style="font-size:13px;font-weight:700;color:#2563eb;margin-bottom:4px">项目经历</h2>
            <div v-for="p in previewData.projects" :key="p.name" style="margin-bottom:6px">
              <strong style="font-size:11px">{{ p.name }}</strong><span style="font-size:9px;color:#888"> · {{ p.techStack }}</span>
              <ul style="margin:2px 0 0 14px;font-size:9px;color:#555;line-height:1.5"><li v-for="h in p.highlights" :key="h">{{ h }}</li></ul>
            </div>
          </div>
          <div v-if="previewData.education?.length" style="margin-bottom:12px">
            <h2 style="font-size:13px;font-weight:700;color:#2563eb;margin-bottom:4px">教育背景</h2>
            <div v-for="e in previewData.education" :key="e.school" style="font-size:10px;margin-bottom:2px;color:#444">
              <strong>{{ e.school }}</strong> · {{ e.major }} · {{ e.degree }} <span style="color:#888">{{ e.start }} - {{ e.end }}</span>
            </div>
          </div>
          <div v-if="previewData.skills?.length">
            <h2 style="font-size:13px;font-weight:700;color:#2563eb;margin-bottom:4px">技能</h2>
            <div style="display:flex;flex-wrap:wrap;gap:3px">
              <span v-for="s in previewData.skills" :key="s.name" style="font-size:9px;background:#eff6ff;color:#2563eb;padding:2px 8px;border-radius:4px">{{ s.name }}</span>
            </div>
          </div>
        </div>
        <div v-else class="flex items-center justify-center h-full text-gray-300 text-sm">点击选项后简历实时预览</div>
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
const personalForm = reactive({ name: '', phone: '', email: '', city: '' })
const status = ref('chatting')
const progress = ref(0)
const jdText = ref('')
const previewData = reactive({ personal:{}, education:[], experience:[], projects:[], skills:[], awards:[], summary:'' })
const chatRef = ref(null)

onMounted(async () => {
  const res = await fetch(`/api/resumes/${resumeId}`)
  const d = await res.json()
  resumeTitle.value = d.data?.title || ''
  await loadNext()
})

const loadNext = async () => {
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
  if (data.module === 'done' || data.status === 'ready') {
    progress.value = 100
    status.value = 'draft'
  } else {
    progress.value = Math.min(90, Math.round(progress.value + 14))
  }
  selectedItems.value = []
  customInput.value = ''
  await nextTick()
  chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })
}

const submitPersonal = async () => {
  await fetch(`/api/resumes/${resumeId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: { personal: { ...personalForm } } }),
  })
  Object.assign(previewData.personal, personalForm)
  loadNext()
}

const submitSelections = async () => {
  if (currentModule.value) {
    await fetch(`/api/resumes/${resumeId}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        selections: { [currentModule.value]: selectedItems.value },
        data: { [currentModule.value]: { selected: selectedItems.value, custom: customInput.value } },
      }),
    })
    if (selectedItems.value.length) updatePreview()
  }
  if (status.value === 'draft') return
  await nextTick()
  chatRef.value?.scrollTo({ top: chatRef.value.scrollHeight, behavior: 'smooth' })
}

const selectSummary = async (o) => {
  await fetch(`/api/resumes/${resumeId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: { summary: o.label } }),
  })
  previewData.summary = o.label
}

const skipModule = () => { selectedItems.value = []; customInput.value = ''; submitSelections() }
const regenerateSummary = () => loadNext()
const optimizeJD = async () => {
  if (!jdText.value.trim()) return
  await fetch(`/api/resumes/${resumeId}/jd-optimize`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jd: jdText.value }) })
  jdText.value = ''
  aiMessage.value = 'JD 已分析完毕！关键词已优化匹配，继续下一步吧。'
}
const updatePreview = () => {
  previewData.personal = previewData.personal || {}
}
</script>

<style scoped>
.ml-13 { margin-left: 52px; }
</style>
