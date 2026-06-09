<template>
  <div class="flex h-[calc(100vh-64px)]">
    <!-- Left sidebar -->
    <div class="w-52 bg-gray-900 text-white flex flex-col shrink-0">
      <div class="p-4">
        <router-link to="/" class="text-gray-400 text-xs hover:text-white transition mb-4 inline-block">← 返回首页</router-link>
        <h2 class="text-sm font-semibold text-gray-300 mt-2">简历编辑</h2>
      </div>
      <nav class="flex-1 px-2 space-y-0.5">
        <button v-for="m in modules" :key="m.key" @click="activeModule = m.key"
          :class="['w-full text-left px-3 py-2.5 rounded-lg text-sm transition flex items-center gap-2', activeModule === m.key ? 'bg-brand-600 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white']">
          <span>{{ m.icon }}</span> {{ m.label }}
        </button>
      </nav>
      <div class="p-3 border-t border-gray-800 space-y-2">
        <button @click="saveResume" class="w-full py-2.5 bg-brand-600 hover:bg-brand-700 rounded-lg text-sm font-medium transition">💾 保存</button>
        <button @click="exportPDF" class="w-full py-2.5 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium transition">📄 导出 PDF</button>
      </div>
    </div>

    <!-- Center Editor -->
    <div class="flex-1 overflow-y-auto p-8 bg-gray-50">
      <div v-if="versions.length" class="mb-6 flex gap-2 flex-wrap">
        <span class="text-xs text-gray-500 mr-2">版本历史：</span>
        <span v-for="(v,i) in versions" :key="i" @click="restoreVersion(i)"
          :class="['px-3 py-1 rounded-full text-xs cursor-pointer transition', currentVersion === i ? 'bg-brand-600 text-white' : 'bg-white border border-gray-200 hover:border-brand-300']">
          v{{ i+1 }}
        </span>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border p-6">
        <!-- Personal -->
        <template v-if="activeModule==='personal'">
          <h2 class="text-lg font-bold mb-5">📋 个人信息</h2>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-xs text-gray-500 mb-1">姓名</label><input v-model="form.personal.name" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
            <div><label class="block text-xs text-gray-500 mb-1">电话</label><input v-model="form.personal.phone" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
            <div><label class="block text-xs text-gray-500 mb-1">邮箱</label><input v-model="form.personal.email" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
            <div><label class="block text-xs text-gray-500 mb-1">城市</label><input v-model="form.personal.city" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
          </div>
        </template>

        <!-- Experience -->
        <template v-if="activeModule==='experience'">
          <div class="flex justify-between items-center mb-5"><h2 class="text-lg font-bold">💼 工作/实习经历</h2><button @click="addItem('experience')" class="text-brand-600 text-sm font-medium hover:underline">+ 添加</button></div>
          <div v-for="(e,i) in form.experience" :key="i" class="mb-6 p-5 border border-gray-200 rounded-xl">
            <div class="grid grid-cols-2 gap-4 mb-3">
              <div><label class="block text-xs text-gray-500 mb-1">公司</label><input v-model="e.company" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">职位</label><input v-model="e.title" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">开始</label><input v-model="e.start" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">结束</label><input v-model="e.end" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
            </div>
            <div class="space-y-2">
              <div v-for="(h,j) in e.highlights" :key="j" class="flex gap-2"><input v-model="e.highlights[j]" :placeholder="'要点 '+(j+1)" class="flex-1 p-2.5 border border-gray-200 rounded-lg text-sm" /><button @click="e.highlights.splice(j,1)" class="text-red-400 text-xs px-2">✕</button></div>
              <button @click="e.highlights.push('')" class="text-brand-600 text-xs font-medium hover:underline">+ 添加要点</button>
            </div>
            <button @click="form.experience.splice(i,1)" class="text-red-500 text-xs mt-3 hover:underline">删除此经历</button>
          </div>
        </template>

        <!-- Projects -->
        <template v-if="activeModule==='projects'">
          <div class="flex justify-between items-center mb-5"><h2 class="text-lg font-bold">📦 项目经历</h2><button @click="addItem('projects')" class="text-brand-600 text-sm font-medium hover:underline">+ 添加</button></div>
          <div v-for="(p,i) in form.projects" :key="i" class="mb-6 p-5 border border-gray-200 rounded-xl">
            <div class="grid grid-cols-2 gap-4 mb-3">
              <div><label class="block text-xs text-gray-500 mb-1">项目名</label><input v-model="p.name" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">角色</label><input v-model="p.role" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div class="col-span-2"><label class="block text-xs text-gray-500 mb-1">技术栈</label><input v-model="p.techStack" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
            </div>
            <div class="space-y-2">
              <div v-for="(h,j) in p.highlights" :key="j" class="flex gap-2"><input v-model="p.highlights[j]" :placeholder="'亮点 '+(j+1)" class="flex-1 p-2.5 border border-gray-200 rounded-lg text-sm" /><button @click="p.highlights.splice(j,1)" class="text-red-400 text-xs px-2">✕</button></div>
              <button @click="p.highlights.push('')" class="text-brand-600 text-xs font-medium hover:underline">+ 添加亮点</button>
            </div>
            <button @click="form.projects.splice(i,1)" class="text-red-500 text-xs mt-3 hover:underline">删除此项目</button>
          </div>
        </template>

        <!-- Education -->
        <template v-if="activeModule==='education'">
          <div class="flex justify-between items-center mb-5"><h2 class="text-lg font-bold">🎓 教育背景</h2><button @click="addItem('education')" class="text-brand-600 text-sm font-medium hover:underline">+ 添加</button></div>
          <div v-for="(e,i) in form.education" :key="i" class="mb-4 p-5 border border-gray-200 rounded-xl">
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs text-gray-500 mb-1">学校</label><input v-model="e.school" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">专业</label><input v-model="e.major" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">学位</label><input v-model="e.degree" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">课程</label><input v-model="e.courses" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">开始</label><input v-model="e.start" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
              <div><label class="block text-xs text-gray-500 mb-1">结束</label><input v-model="e.end" class="w-full p-2.5 border border-gray-200 rounded-lg text-sm" /></div>
            </div>
            <button @click="form.education.splice(i,1)" class="text-red-500 text-xs mt-3 hover:underline">删除</button>
          </div>
        </template>

        <!-- Other modules -->
        <template v-if="activeModule==='skills'">
          <h2 class="text-lg font-bold mb-5">🛠️ 技能</h2>
          <div class="space-y-3">
            <div v-for="(s,i) in form.skills" :key="i" class="flex gap-3">
              <input v-model="s.name" placeholder="技能名" class="flex-1 p-2.5 border border-gray-200 rounded-lg text-sm" />
              <select v-model="s.level" class="w-24 p-2.5 border border-gray-200 rounded-lg text-sm"><option>精通</option><option>熟练</option><option>了解</option></select>
              <button @click="form.skills.splice(i,1)" class="text-red-400 px-2">✕</button>
            </div>
            <button @click="form.skills.push({name:'',level:'熟练'})" class="text-brand-600 text-sm font-medium hover:underline">+ 添加</button>
          </div>
        </template>
        <template v-if="activeModule==='awards'">
          <h2 class="text-lg font-bold mb-5">🏆 奖项荣誉</h2>
          <div class="space-y-3">
            <div v-for="(a,i) in form.awards" :key="i" class="flex gap-3">
              <input v-model="a.name" placeholder="奖项名称" class="flex-1 p-2.5 border border-gray-200 rounded-lg text-sm" />
              <input v-model="a.level" placeholder="级别" class="w-24 p-2.5 border border-gray-200 rounded-lg text-sm" />
              <input v-model="a.date" placeholder="日期" class="w-32 p-2.5 border border-gray-200 rounded-lg text-sm" />
              <button @click="form.awards.splice(i,1)" class="text-red-400 px-2">✕</button>
            </div>
            <button @click="form.awards.push({name:'',level:'',date:''})" class="text-brand-600 text-sm font-medium hover:underline">+ 添加</button>
          </div>
        </template>
        <template v-if="activeModule==='summary'">
          <h2 class="text-lg font-bold mb-5">📝 自我评价</h2>
          <textarea v-model="form.summary" rows="6" class="w-full p-4 border border-gray-200 rounded-xl text-sm resize-none" placeholder="介绍自己的优势..."></textarea>
        </template>
      </div>
    </div>

    <!-- Right Preview -->
    <div class="w-80 bg-gray-100 p-4 overflow-y-auto flex items-start justify-center shrink-0">
      <div class="bg-white shadow-xl rounded-sm sticky top-4" style="width:210mm; min-height:297mm; padding:15mm; transform:scale(0.45); transform-origin:top center;">
        <div style="font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:2px">{{ form.personal?.name || '姓名' }}</div>
        <div style="font-size:8px;color:#666;margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #2563eb">{{ [form.personal?.phone, form.personal?.email, form.personal?.city].filter(Boolean).join(' · ') }}</div>
        <div v-if="form.summary" style="margin-bottom:10px"><div style="font-size:11px;font-weight:700;color:#2563eb;margin-bottom:2px">自我评价</div><div style="font-size:8px;color:#444;line-height:1.5">{{ form.summary }}</div></div>
        <div v-if="form.experience?.length" style="margin-bottom:10px">
          <div style="font-size:11px;font-weight:700;color:#2563eb;margin-bottom:2px">工作经历</div>
          <div v-for="e in form.experience" :key="e.company" style="margin-bottom:6px">
            <div style="display:flex;justify-content:space-between"><strong style="font-size:9px">{{ e.title || '职位' }}</strong><span style="font-size:7px;color:#888">{{ e.start }} - {{ e.end }}</span></div>
            <div style="font-size:8px;color:#555">{{ e.company }}</div>
            <ul style="margin:1px 0 0 12px;font-size:7px;color:#555;line-height:1.4"><li v-for="h in e.highlights" :key="h">{{ h }}</li></ul>
          </div>
        </div>
        <div v-if="form.projects?.length" style="margin-bottom:10px">
          <div style="font-size:11px;font-weight:700;color:#2563eb;margin-bottom:2px">项目经历</div>
          <div v-for="p in form.projects" :key="p.name" style="margin-bottom:4px"><strong style="font-size:9px">{{ p.name }}</strong><span style="font-size:7px;color:#888"> · {{ p.techStack }}</span></div>
        </div>
        <div v-if="form.education?.length" style="margin-bottom:10px">
          <div style="font-size:11px;font-weight:700;color:#2563eb;margin-bottom:2px">教育背景</div>
          <div v-for="e in form.education" :key="e.school" style="font-size:8px;color:#444;margin-bottom:1px"><strong>{{ e.school }}</strong> · {{ e.major }} · {{ e.degree }}</div>
        </div>
        <div v-if="form.skills?.length">
          <div style="font-size:11px;font-weight:700;color:#2563eb;margin-bottom:2px">技能</div>
          <div style="display:flex;flex-wrap:wrap;gap:2px"><span v-for="s in form.skills" :key="s.name" style="font-size:7px;background:#eff6ff;color:#2563eb;padding:1px 6px;border-radius:3px">{{ s.name }}</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const resumeId = route.params.id
const activeModule = ref('personal')
const currentVersion = ref(0)
const versions = ref([])
const modules = [
  { key:'personal', icon:'📋', label:'个人信息' }, { key:'education', icon:'🎓', label:'教育背景' },
  { key:'awards', icon:'🏆', label:'奖项荣誉' }, { key:'experience', icon:'💼', label:'工作经历' },
  { key:'projects', icon:'📦', label:'项目经历' }, { key:'skills', icon:'🛠️', label:'技能' },
  { key:'summary', icon:'📝', label:'自我评价' },
]
const form = reactive({ personal:{name:'',phone:'',email:'',city:''}, education:[], awards:[], experience:[], projects:[], skills:[], summary:'' })

onMounted(async () => {
  try {
    const res = await fetch(`/api/resumes/${resumeId}`)
    const d = await res.json()
    if (d.data?.data) {
      const data = typeof d.data.data === 'string' ? JSON.parse(d.data.data) : d.data.data
      Object.assign(form, data)
    }
    saveVersion()
  } catch(e) {}
})

const addItem = (key) => {
  const d = { education:{school:'',major:'',degree:'',start:'',end:'',courses:''}, experience:{company:'',title:'',start:'',end:'',highlights:['','','']}, projects:{name:'',role:'',techStack:'',highlights:['','','']} }
  form[key].push(d[key]||{})
}
const saveVersion = () => { versions.value.push(JSON.parse(JSON.stringify(form))); currentVersion.value = versions.value.length - 1 }
const restoreVersion = (i) => { Object.assign(form, JSON.parse(JSON.stringify(versions.value[i]))); currentVersion.value = i }
const saveResume = async () => {
  await fetch(`/api/resumes/${resumeId}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({data:JSON.stringify(form),status:'done'}) })
  saveVersion(); alert('已保存')
}
const exportPDF = async () => {
  const res = await fetch(`/api/resumes/${resumeId}/export?format=html`)
  const html = await res.text(); const w = window.open('','_blank'); w.document.write(html); w.document.close(); setTimeout(()=>w.print(),500)
}
</script>
