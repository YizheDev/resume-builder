<template>
  <div class="max-w-6xl mx-auto py-12 px-4">
    <h1 class="text-3xl font-bold text-center mb-2">选择简历模板</h1>
    <p class="text-gray-500 text-center mb-10">选择一套模板，开始制作你的专业简历</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      <div
        v-for="t in templates"
        :key="t.id"
        @click="createResume(t.id)"
        class="bg-white rounded-xl shadow-sm hover:shadow-md transition cursor-pointer overflow-hidden border"
      >
        <div :class="t.bgClass" class="h-40 flex items-center justify-center text-white text-lg font-bold">
          {{ t.name }}
        </div>
        <div class="p-4">
          <h3 class="font-semibold">{{ t.name }}</h3>
          <p class="text-sm text-gray-500 mt-1">{{ t.desc }}</p>
        </div>
      </div>
    </div>

    <!-- 已有简历 -->
    <div v-if="resumes.length > 0">
      <h2 class="text-xl font-semibold mb-4">已创建的简历</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="r in resumes"
          :key="r.id"
          @click="$router.push(`/editor/${r.id}`)"
          class="bg-white rounded-lg p-4 shadow-sm hover:shadow cursor-pointer border"
        >
          <h4 class="font-medium">{{ r.title }}</h4>
          <p class="text-xs text-gray-400 mt-1">{{ r.updated_at?.slice(0, 10) }}</p>
          <button @click.stop="deleteResume(r.id)" class="text-red-400 text-xs mt-2 hover:underline">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const templates = [
  { id: 'classic', name: '经典通用', desc: '应届生 / 实习生', bgClass: 'bg-blue-600' },
  { id: 'professional', name: '专业简约', desc: '社招 / 经验丰富', bgClass: 'bg-gray-800' },
  { id: 'tech', name: '技术岗', desc: '程序员 / 工程师', bgClass: 'bg-indigo-700' },
  { id: 'minimal', name: '现代极简', desc: '设计师 / 创意岗', bgClass: 'bg-slate-600' },
  { id: 'english', name: '英文简历', desc: '外企 / 留学申请', bgClass: 'bg-emerald-600' },
]

const resumes = ref([])

onMounted(async () => {
  try {
    const res = await fetch('/api/resumes')
    const data = await res.json()
    resumes.value = data.data || []
  } catch (e) { /* 忽略 */ }
})

const createResume = async (templateId) => {
  const res = await fetch('/api/resumes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: '未命名简历', template: templateId, data: '{}' })
  })
  const data = await res.json()
  router.push(`/editor/${data.data.id}`)
}

const deleteResume = async (id) => {
  await fetch(`/api/resumes/${id}`, { method: 'DELETE' })
  resumes.value = resumes.value.filter(r => r.id !== id)
}
</script>
