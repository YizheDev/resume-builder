<template>
  <div>
    <!-- Hero -->
    <section class="bg-gradient-to-br from-brand-50 via-white to-blue-50 py-20">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
          求职写简历，AI 帮你 <span class="text-brand-600">3 分钟搞定</span>
        </h1>
        <p class="text-lg text-gray-500 mb-10 max-w-2xl mx-auto">
          不知道怎么写简历？告诉我你的背景，AI 智能推荐岗位 + 自动生成专业简历，点点手指就能完成
        </p>

        <!-- 输入区 -->
        <div class="bg-white rounded-2xl shadow-lg shadow-gray-200/50 p-6 text-left max-w-2xl mx-auto">
          <label class="block text-sm font-medium text-gray-700 mb-3">
            ✨ 介绍一下你自己（越详细越好）
          </label>
          <textarea
            v-model="background"
            rows="4"
            class="w-full p-4 border border-gray-200 rounded-xl text-sm resize-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
            placeholder="例如：我是 XX 大学计算机科学专业大四学生，会 Python 和 Java，做过一个电商网站课程设计，参加过 ACM 竞赛..."
          ></textarea>
          <div class="flex gap-3 mt-4">
            <button
              @click="analyze"
              :disabled="loading || !background.trim()"
              class="flex-1 py-3.5 bg-brand-600 text-white rounded-xl font-medium hover:bg-brand-700 disabled:opacity-50 transition text-base"
            >
              {{ loading ? 'AI 分析中...' : '✨ 免费生成专业简历' }}
            </button>
            <button
              @click="quickDemo"
              class="px-6 py-3.5 border-2 border-gray-200 rounded-xl font-medium text-gray-500 hover:border-brand-300 hover:text-brand-600 transition text-sm"
            >
              看个示例
            </button>
          </div>
        </div>

        <!-- 统计 -->
        <div class="flex justify-center gap-12 mt-12 text-sm text-gray-400">
          <div class="text-center">
            <div class="text-2xl font-bold text-brand-600">6</div>
            <div>推荐岗位方向</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-brand-600">7</div>
            <div>简历内容模块</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-brand-600">3 分钟</div>
            <div>快速生成简历</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="py-20 bg-white">
      <div class="max-w-6xl mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">三步创建专业简历</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center p-8 rounded-2xl bg-gradient-to-b from-brand-50 to-white border border-brand-100">
            <div class="w-12 h-12 bg-brand-600 text-white rounded-xl flex items-center justify-center text-xl mx-auto mb-4">1</div>
            <h3 class="text-lg font-semibold mb-2">AI 推荐岗位</h3>
            <p class="text-sm text-gray-500">输入背景，AI 智能分析并推荐最适合你的岗位方向，支持多选</p>
          </div>
          <div class="text-center p-8 rounded-2xl bg-gradient-to-b from-blue-50 to-white border border-blue-100">
            <div class="w-12 h-12 bg-blue-600 text-white rounded-xl flex items-center justify-center text-xl mx-auto mb-4">2</div>
            <h3 class="text-lg font-semibold mb-2">勾选式填写</h3>
            <p class="text-sm text-gray-500">不用写大段文字，AI 列出高质量选项，你只需勾选 + 确认</p>
          </div>
          <div class="text-center p-8 rounded-2xl bg-gradient-to-b from-green-50 to-white border border-green-100">
            <div class="w-12 h-12 bg-green-600 text-white rounded-xl flex items-center justify-center text-xl mx-auto mb-4">3</div>
            <h3 class="text-lg font-semibold mb-2">一键导出 PDF</h3>
            <p class="text-sm text-gray-500">生成后手动微调，满意即可导出 A4 专业简历 PDF</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 推荐结果 -->
    <section v-if="recommendations.length > 0" class="py-16 bg-gray-50">
      <div class="max-w-4xl mx-auto px-4">
        <h2 class="text-2xl font-bold text-center mb-2">🎯 AI 推荐以下岗位</h2>
        <p class="text-gray-500 text-center mb-8">选择你感兴趣的，可多选同时生成多份简历</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="r in recommendations"
            :key="r.role"
            @click="toggleRole(r)"
            :class="['p-5 rounded-xl border-2 cursor-pointer transition-all', selectedRoles.includes(r.role) ? 'border-brand-500 bg-brand-50 shadow-md' : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm']"
          >
            <div class="flex justify-between items-start mb-2">
              <span class="font-semibold text-lg">{{ r.role }}</span>
              <span class="px-2.5 py-1 rounded-full text-xs font-bold" :class="r.score >= 85 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
                {{ r.score }}% 匹配
              </span>
            </div>
            <p class="text-sm text-gray-500 mb-3">{{ r.reason }}</p>
            <div class="flex flex-wrap gap-1.5">
              <span v-for="s in r.skills?.slice(0,5)" :key="s" class="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full">{{ s }}</span>
            </div>
          </div>
        </div>
        <button
          v-if="selectedRoles.length > 0"
          @click="startGenerate"
          class="mt-8 w-full py-4 bg-brand-600 text-white rounded-xl font-semibold text-lg hover:bg-brand-700 transition shadow-lg shadow-brand-200"
        >
          开始生成 {{ selectedRoles.length }} 份简历 →
        </button>
      </div>
    </section>
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
    if (recommendations.value.length > 0) {
      document.querySelector('section').scrollIntoView({ behavior: 'smooth' })
    }
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
  background.value = '清华大学软件工程大四，熟练掌握Vue和Python，在字节跳动实习过前端开发，做过校园二手交易平台，参加过蓝桥杯获得省二等奖'
  analyze()
}
</script>
