<template>
  <div class="max-w-3xl mx-auto py-20 px-4">
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold mb-3">AI 简历生成器</h1>
      <p class="text-lg text-gray-500">不知道怎么写简历？告诉我你的背景，AI 帮你搞定一切</p>
    </div>

    <div class="bg-white rounded-2xl shadow-sm p-8 border">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        介绍一下你自己（越详细越好）
      </label>
      <textarea
        v-model="background"
        rows="5"
        class="w-full p-4 border border-gray-200 rounded-xl text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="例如：我是 XX 大学计算机科学专业大四学生，会 Python 和 Java，做过一个电商网站课程设计，参加过 ACM 竞赛..."
      ></textarea>

      <div class="mt-6 flex gap-3 justify-center">
        <button
          @click="analyze"
          :disabled="loading || !background.trim()"
          class="px-8 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {{ loading ? 'AI 分析中...' : '✨ AI 分析推荐岗位' }}
        </button>
        <button
          @click="quickDemo"
          class="px-8 py-3 border border-gray-200 rounded-xl font-medium text-gray-600 hover:bg-gray-50 transition"
        >
          👀 快速预览
        </button>
      </div>

      <!-- 推荐结果 -->
      <div v-if="recommendations.length > 0" class="mt-10">
        <h2 class="text-xl font-semibold mb-4">🎯 AI 推荐以下岗位（可多选）</h2>
        <div class="grid grid-cols-2 gap-3">
          <div
            v-for="r in recommendations"
            :key="r.role"
            @click="toggleRole(r)"
            :class="['p-4 rounded-xl border-2 cursor-pointer transition', selectedRoles.includes(r.role) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300']"
          >
            <div class="flex justify-between items-center">
              <span class="font-semibold">{{ r.role }}</span>
              <span class="text-sm font-bold" :class="r.score >= 80 ? 'text-green-600' : 'text-yellow-600'">{{ r.score }}%</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ r.reason }}</p>
            <div class="flex flex-wrap gap-1 mt-2">
              <span v-for="s in r.skills?.slice(0,4)" :key="s" class="text-xs bg-gray-100 px-2 py-0.5 rounded">{{ s }}</span>
            </div>
          </div>
        </div>

        <button
          v-if="selectedRoles.length > 0"
          @click="startGenerate"
          class="mt-6 w-full py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition"
        >
          开始生成 {{ selectedRoles.length }} 份简历 →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const background = ref('')
const loading = ref(false)
const recommendations = ref([])
const selectedRoles = ref([])

const analyze = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/analyze', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ background: background.value }),
    })
    const data = await res.json()
    recommendations.value = data.data?.recommendations || []
  } catch (e) { alert('分析失败，请重试') }
  finally { loading.value = false }
}

const toggleRole = (r) => {
  const idx = selectedRoles.value.indexOf(r.role)
  idx >= 0 ? selectedRoles.value.splice(idx, 1) : selectedRoles.value.push(r.role)
}

const startGenerate = async () => {
  for (const role of selectedRoles.value) {
    const res = await fetch('/api/resumes', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, title: `${role} - 简历` }),
    })
    const d = await res.json()
    if (d.data?.id) router.push(`/chat/${d.data.id}`)
  }
}

const quickDemo = () => {
  background.value = 'XX大学 软件工程 大四 熟悉Vue和Python 做过校园二手交易平台 参加过蓝桥杯'
  analyze()
}
</script>
