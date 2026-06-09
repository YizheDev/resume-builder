<template>
  <div class="flex h-screen">
    <!-- 左侧：表单 -->
    <div class="w-1/2 overflow-y-auto p-6 border-r">
      <div class="flex items-center justify-between mb-6">
        <button @click="$router.push('/')" class="text-gray-500 hover:text-gray-700">← 返回</button>
        <button @click="saveResume" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">保存</button>
      </div>

      <input v-model="form.title" class="text-xl font-bold w-full mb-6 p-2 border rounded" placeholder="简历标题" />

      <!-- 个人信息 -->
      <Section title="📋 个人信息">
        <input v-model="form.data.personal.name" placeholder="姓名" class="field" />
        <input v-model="form.data.personal.phone" placeholder="电话" class="field" />
        <input v-model="form.data.personal.email" placeholder="邮箱" class="field" />
        <input v-model="form.data.personal.address" placeholder="地址" class="field" />
      </Section>

      <!-- 教育背景 -->
      <Section title="🎓 教育背景">
        <div v-for="(edu, i) in form.data.education" :key="i" class="mb-3 p-3 bg-gray-50 rounded">
          <input v-model="edu.school" placeholder="学校" class="field" />
          <input v-model="edu.major" placeholder="专业" class="field" />
          <input v-model="edu.degree" placeholder="学位" class="field" />
          <input v-model="edu.start" placeholder="开始时间" class="field w-1/2 inline" />
          <input v-model="edu.end" placeholder="结束时间" class="field w-1/2 inline" />
        </div>
        <button @click="addEducation" class="text-blue-600 text-sm">+ 添加教育经历</button>
      </Section>

      <!-- 工作经历 -->
      <Section title="💼 工作经历">
        <div v-for="(exp, i) in form.data.experience" :key="i" class="mb-3 p-3 bg-gray-50 rounded">
          <input v-model="exp.company" placeholder="公司" class="field" />
          <input v-model="exp.title" placeholder="职位" class="field" />
          <input v-model="exp.start" placeholder="开始时间" class="field w-1/2 inline" />
          <input v-model="exp.end" placeholder="结束时间" class="field w-1/2 inline" />
          <textarea v-model="exp.description" placeholder="工作描述" class="field" rows="3"></textarea>
        </div>
        <button @click="addExperience" class="text-blue-600 text-sm">+ 添加工作经历</button>
      </Section>

      <!-- 技能 -->
      <Section title="🛠️ 技能">
        <div v-for="(skill, i) in form.data.skills" :key="i" class="flex gap-2 mb-2">
          <input v-model="skill.name" placeholder="技能名称" class="field flex-1" />
          <input v-model="skill.level" placeholder="熟练度" class="field w-24" />
        </div>
        <button @click="addSkill" class="text-blue-600 text-sm">+ 添加技能</button>
      </Section>

      <!-- 自我评价 -->
      <Section title="📝 自我评价">
        <textarea v-model="form.data.summary" placeholder="简要介绍自己..." class="field" rows="4"></textarea>
      </Section>
    </div>

    <!-- 右侧：预览 -->
    <div class="w-1/2 bg-gray-200 p-6 overflow-y-auto">
      <div class="bg-white shadow-lg mx-auto" style="width:210mm; min-height:297mm; padding:20mm;">
        <ResumePreview :data="form.data" :template="form.template" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Section from '../components/Section.vue'
import ResumePreview from '../components/ResumePreview.vue'

const route = useRoute()
const form = ref({
  title: '未命名简历',
  template: 'classic',
  data: {
    personal: { name: '', phone: '', email: '', address: '' },
    education: [],
    experience: [],
    skills: [],
    summary: '',
  }
})

onMounted(async () => {
  if (route.params.id && route.params.id !== 'new') {
    const res = await fetch(`/api/resumes/${route.params.id}`)
    const d = await res.json()
    if (d.data) {
      form.value.title = d.data.title
      form.value.template = d.data.template
      form.value.data = typeof d.data.data === 'string' ? JSON.parse(d.data.data) : d.data.data
    }
  }
})

const saveResume = async () => {
  const payload = {
    title: form.value.title,
    template: form.value.template,
    data: JSON.stringify(form.value.data),
  }
  if (route.params.id && route.params.id !== 'new') {
    await fetch(`/api/resumes/${route.params.id}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    })
  } else {
    const res = await fetch('/api/resumes', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    })
    const d = await res.json()
    route.params.id = d.data.id
  }
  alert('已保存')
}

const addEducation = () => form.value.data.education.push({ school: '', major: '', degree: '', start: '', end: '' })
const addExperience = () => form.value.data.experience.push({ company: '', title: '', start: '', end: '', description: '' })
const addSkill = () => form.value.data.skills.push({ name: '', level: '' })
</script>

<style scoped>
.field { @apply w-full p-2 border border-gray-200 rounded mb-2 text-sm; }
</style>
