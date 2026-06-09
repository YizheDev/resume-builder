<template>
  <div class="flex h-screen">
    <!-- 左侧模块导航 -->
    <div class="w-48 bg-gray-900 text-white p-4 flex flex-col">
      <router-link to="/" class="text-gray-400 text-sm hover:text-white mb-6">← 返回首页</router-link>
      <div v-for="m in modules" :key="m.key" @click="activeModule = m.key"
        :class="['px-3 py-2 rounded-lg text-sm cursor-pointer mb-1 transition', activeModule === m.key ? 'bg-blue-600' : 'hover:bg-gray-800']">
        {{ m.icon }} {{ m.label }}
      </div>
      <div class="mt-auto pt-4 border-t border-gray-700 space-y-2">
        <button @click="saveResume" class="w-full py-2 bg-blue-600 rounded-lg text-sm hover:bg-blue-700">💾 保存</button>
        <button @click="exportPDF" class="w-full py-2 bg-green-600 rounded-lg text-sm hover:bg-green-700">📄 导出 PDF</button>
      </div>
    </div>

    <!-- 中间编辑区 -->
    <div class="flex-1 overflow-y-auto p-6">
      <!-- 版本历史 -->
      <div v-if="versions.length > 0" class="mb-4 flex gap-2 flex-wrap">
        <span v-for="(v, i) in versions" :key="i" @click="restoreVersion(i)"
          :class="['px-3 py-1 rounded-full text-xs cursor-pointer', currentVersion === i ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200']">
          v{{ i + 1 }}
        </span>
      </div>

      <!-- 个人信息 -->
      <div v-if="activeModule === 'personal'" class="space-y-3">
        <h2 class="text-lg font-semibold mb-4">📋 个人信息</h2>
        <input v-model="form.personal.name" placeholder="姓名" class="w-full p-2 border rounded-lg" />
        <div class="grid grid-cols-2 gap-3">
          <input v-model="form.personal.phone" placeholder="电话" class="p-2 border rounded-lg" />
          <input v-model="form.personal.email" placeholder="邮箱" class="p-2 border rounded-lg" />
          <input v-model="form.personal.city" placeholder="城市" class="p-2 border rounded-lg" />
          <input v-model="form.personal.linkedin" placeholder="LinkedIn / GitHub" class="p-2 border rounded-lg" />
        </div>
      </div>

      <!-- 教育背景 -->
      <div v-if="activeModule === 'education'" class="space-y-3">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">🎓 教育背景</h2>
          <button @click="addItem('education')" class="text-blue-600 text-sm hover:underline">+ 添加</button>
        </div>
        <div v-for="(e, i) in form.education" :key="i" class="p-4 border rounded-xl space-y-2">
          <div class="grid grid-cols-2 gap-3">
            <input v-model="e.school" placeholder="学校" class="p-2 border rounded-lg" />
            <input v-model="e.major" placeholder="专业" class="p-2 border rounded-lg" />
            <input v-model="e.degree" placeholder="学位" class="p-2 border rounded-lg" />
            <input v-model="e.courses" placeholder="相关课程" class="p-2 border rounded-lg" />
            <input v-model="e.start" placeholder="开始时间" class="p-2 border rounded-lg" />
            <input v-model="e.end" placeholder="结束时间" class="p-2 border rounded-lg" />
          </div>
          <button @click="form.education.splice(i,1)" class="text-red-400 text-xs hover:underline">删除</button>
        </div>
      </div>

      <!-- 工作经历 -->
      <div v-if="activeModule === 'experience'" class="space-y-3">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">💼 工作/实习经历</h2>
          <button @click="addItem('experience')" class="text-blue-600 text-sm hover:underline">+ 添加</button>
        </div>
        <div v-for="(e, i) in form.experience" :key="i" class="p-4 border rounded-xl space-y-2">
          <div class="grid grid-cols-2 gap-3">
            <input v-model="e.company" placeholder="公司" class="p-2 border rounded-lg" />
            <input v-model="e.title" placeholder="职位" class="p-2 border rounded-lg" />
            <input v-model="e.start" placeholder="开始时间" class="p-2 border rounded-lg" />
            <input v-model="e.end" placeholder="结束时间" class="p-2 border rounded-lg" />
          </div>
          <div v-for="(h, j) in e.highlights" :key="j" class="flex gap-2">
            <input v-model="e.highlights[j]" :placeholder="'要点 '+(j+1)" class="flex-1 p-2 border rounded-lg text-sm" />
            <button @click="e.highlights.splice(j,1)" class="text-red-400 text-xs">✕</button>
          </div>
          <button @click="e.highlights.push('')" class="text-blue-500 text-xs hover:underline">+ 添加要点</button>
          <button @click="form.experience.splice(i,1)" class="text-red-400 text-xs hover:underline ml-4">删除</button>
        </div>
      </div>

      <!-- 项目经历 -->
      <div v-if="activeModule === 'projects'" class="space-y-3">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">📦 项目经历</h2>
          <button @click="addItem('projects')" class="text-blue-600 text-sm hover:underline">+ 添加</button>
        </div>
        <div v-for="(p, i) in form.projects" :key="i" class="p-4 border rounded-xl space-y-2">
          <div class="grid grid-cols-2 gap-3">
            <input v-model="p.name" placeholder="项目名称" class="p-2 border rounded-lg" />
            <input v-model="p.role" placeholder="角色" class="p-2 border rounded-lg" />
            <input v-model="p.techStack" placeholder="技术栈" class="p-2 border rounded-lg col-span-2" />
          </div>
          <div v-for="(h, j) in p.highlights" :key="j" class="flex gap-2">
            <input v-model="p.highlights[j]" :placeholder="'亮点 '+(j+1)" class="flex-1 p-2 border rounded-lg text-sm" />
            <button @click="p.highlights.splice(j,1)" class="text-red-400 text-xs">✕</button>
          </div>
          <button @click="p.highlights.push('')" class="text-blue-500 text-xs hover:underline">+ 添加亮点</button>
          <button @click="form.projects.splice(i,1)" class="text-red-400 text-xs hover:underline ml-4">删除</button>
        </div>
      </div>

      <!-- 技能 -->
      <div v-if="activeModule === 'skills'" class="space-y-3">
        <h2 class="text-lg font-semibold mb-4">🛠️ 技能</h2>
        <div v-for="(s, i) in form.skills" :key="i" class="flex gap-2">
          <input v-model="s.name" placeholder="技能名称" class="flex-1 p-2 border rounded-lg" />
          <select v-model="s.level" class="w-24 p-2 border rounded-lg text-sm">
            <option>精通</option><option>熟练</option><option>了解</option>
          </select>
          <button @click="form.skills.splice(i,1)" class="text-red-400">✕</button>
        </div>
        <button @click="form.skills.push({name:'',level:'熟练'})" class="text-blue-600 text-sm hover:underline">+ 添加技能</button>
      </div>

      <!-- 其他模块同理简化 -->
      <div v-if="activeModule === 'awards'" class="space-y-3">
        <h2 class="text-lg font-semibold mb-4">🏆 奖项荣誉</h2>
        <div v-for="(a, i) in form.awards" :key="i" class="flex gap-2">
          <input v-model="a.name" placeholder="奖项名称" class="flex-1 p-2 border rounded-lg" />
          <input v-model="a.level" placeholder="级别" class="w-24 p-2 border rounded-lg" />
          <input v-model="a.date" placeholder="日期" class="w-32 p-2 border rounded-lg" />
          <button @click="form.awards.splice(i,1)" class="text-red-400">✕</button>
        </div>
        <button @click="form.awards.push({name:'',level:'',date:''})" class="text-blue-600 text-sm hover:underline">+ 添加</button>
      </div>

      <div v-if="activeModule === 'summary'" class="space-y-3">
        <h2 class="text-lg font-semibold mb-4">📝 自我评价</h2>
        <textarea v-model="form.summary" rows="5" class="w-full p-3 border rounded-lg" placeholder="介绍自己..."></textarea>
      </div>
    </div>

    <!-- 右侧预览 -->
    <div class="w-96 bg-gray-200 p-4 overflow-y-auto">
      <div class="bg-white shadow mx-auto p-6 text-xs" style="width:210mm; min-height:297mm; transform:scale(0.55); transform-origin:top left;">
        <h1 style="font-size:18px;margin-bottom:2px">{{ form.personal?.name || '姓名' }}</h1>
        <p style="font-size:10px;color:#666;margin-bottom:12px">{{ [form.personal?.phone, form.personal?.email, form.personal?.city].filter(Boolean).join(' · ') }}</p>
        <div v-if="form.experience?.length">
          <h2 style="font-size:13px;border-bottom:1px solid #ddd;padding-bottom:2px;margin:10px 0 6px">工作经历</h2>
          <div v-for="e in form.experience" :key="e.company" style="margin-bottom:6px">
            <strong>{{ e.title || '职位' }}</strong> — {{ e.company }}<br>
            <span style="color:#666">{{ e.start }} - {{ e.end }}</span>
            <ul style="margin:2px 0 0 12px"><li v-for="h in e.highlights" :key="h">{{ h }}</li></ul>
          </div>
        </div>
        <div v-if="form.projects?.length">
          <h2 style="font-size:13px;border-bottom:1px solid #ddd;padding-bottom:2px;margin:10px 0 6px">项目经历</h2>
          <div v-for="p in form.projects" :key="p.name"><strong>{{ p.name }}</strong> · {{ p.techStack }}</div>
        </div>
        <div v-if="form.education?.length">
          <h2 style="font-size:13px;border-bottom:1px solid #ddd;padding-bottom:2px;margin:10px 0 6px">教育背景</h2>
          <div v-for="e in form.education" :key="e.school"><strong>{{ e.school }}</strong> · {{ e.major }} · {{ e.degree }}</div>
        </div>
        <div v-if="form.skills?.length">
          <h2 style="font-size:13px;border-bottom:1px solid #ddd;padding-bottom:2px;margin:10px 0 6px">技能</h2>
          <span v-for="s in form.skills" :key="s.name" style="background:#f0f0f0;padding:1px 6px;margin:1px;border-radius:3px;font-size:10px">{{ s.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const resumeId = route.params.id
const activeModule = ref('personal')
const currentVersion = ref(0)
const versions = ref([])

const modules = [
  { key: 'personal', icon: '📋', label: '个人信息' },
  { key: 'education', icon: '🎓', label: '教育背景' },
  { key: 'awards', icon: '🏆', label: '奖项荣誉' },
  { key: 'experience', icon: '💼', label: '工作经历' },
  { key: 'projects', icon: '📦', label: '项目经历' },
  { key: 'skills', icon: '🛠️', label: '技能' },
  { key: 'summary', icon: '📝', label: '自我评价' },
]

const form = reactive({
  personal: { name: '', phone: '', email: '', city: '', linkedin: '' },
  education: [],
  awards: [],
  experience: [],
  projects: [],
  skills: [],
  summary: '',
})

onMounted(async () => {
  const res = await fetch(`/api/resumes/${resumeId}`)
  const d = await res.json()
  if (d.data?.data) {
    const data = typeof d.data.data === 'string' ? JSON.parse(d.data.data) : d.data.data
    Object.assign(form, data)
  }
  saveVersion()
})

const addItem = (key) => {
  const defaults = {
    education: { school: '', major: '', degree: '', start: '', end: '', courses: '' },
    experience: { company: '', title: '', start: '', end: '', highlights: ['', '', ''] },
    projects: { name: '', role: '', techStack: '', highlights: ['', '', ''] },
  }
  form[key].push(defaults[key] || {})
}

const saveVersion = () => {
  versions.value.push({ ...JSON.parse(JSON.stringify(form)) })
  currentVersion.value = versions.value.length - 1
}

const restoreVersion = (i) => {
  Object.assign(form, JSON.parse(JSON.stringify(versions.value[i])))
  currentVersion.value = i
}

const saveResume = async () => {
  await fetch(`/api/resumes/${resumeId}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: JSON.stringify(form), status: 'done' }),
  })
  saveVersion()
  alert('已保存')
}

const exportPDF = async () => {
  const res = await fetch(`/api/resumes/${resumeId}/export?format=html&lang=cn`)
  const html = await res.text()
  const w = window.open('', '_blank')
  w.document.write(html)
  w.document.close()
  setTimeout(() => w.print(), 500)
}
</script>
