<template>
  <div class="text-sm leading-relaxed" id="resume-preview">
    <!-- Classic Template -->
    <div v-if="template === 'classic'">
      <div class="bg-blue-700 text-white p-6 -m-8 mb-6">
        <h1 class="text-2xl font-bold">{{ data.personal?.name || '姓名' }}</h1>
        <p class="text-blue-100 text-xs mt-2">{{ [data.personal?.phone, data.personal?.email, data.personal?.address].filter(Boolean).join(' | ') }}</p>
      </div>
      <div class="grid grid-cols-3 gap-6">
        <div>
          <Section title="教育背景">
            <div v-for="e in data.education" :key="e.school" class="mb-2">
              <p class="font-semibold">{{ e.school }}</p>
              <p class="text-gray-600 text-xs">{{ e.major }} · {{ e.degree }}</p>
              <p class="text-gray-400 text-xs">{{ e.start }} - {{ e.end }}</p>
            </div>
          </Section>
          <Section title="技能">
            <div v-for="s in data.skills" :key="s.name" class="mb-1">
              <span>{{ s.name }}</span>
              <span class="text-gray-400 text-xs ml-2">{{ s.level }}</span>
            </div>
          </Section>
        </div>
        <div class="col-span-2">
          <Section title="工作经历">
            <div v-for="e in data.experience" :key="e.company" class="mb-3">
              <p class="font-semibold">{{ e.company }} · {{ e.title }}</p>
              <p class="text-gray-400 text-xs">{{ e.start }} - {{ e.end }}</p>
              <p class="text-gray-600 mt-1 text-xs">{{ e.description }}</p>
            </div>
          </Section>
          <Section v-if="data.summary" title="自我评价">
            <p class="text-gray-600 text-xs">{{ data.summary }}</p>
          </Section>
        </div>
      </div>
    </div>

    <!-- Professional Template -->
    <div v-else-if="template === 'professional'">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold">{{ data.personal?.name || '姓名' }}</h1>
        <p class="text-gray-500 text-xs mt-1">{{ [data.personal?.phone, data.personal?.email, data.personal?.address].filter(Boolean).join(' · ') }}</p>
      </div>
      <hr class="mb-4" />
      <Section v-if="data.summary" title="个人总结">
        <p class="text-xs">{{ data.summary }}</p>
      </Section>
      <Section title="工作经历">
        <div v-for="e in data.experience" :key="e.company" class="mb-3">
          <p class="font-semibold">{{ e.title }} — {{ e.company }}</p>
          <p class="text-gray-400 text-xs">{{ e.start }} - {{ e.end }}</p>
          <p class="mt-1 text-xs">{{ e.description }}</p>
        </div>
      </Section>
      <Section title="教育背景">
        <div v-for="e in data.education" :key="e.school" class="mb-1">
          <span class="font-semibold">{{ e.school }}</span>
          <span class="text-gray-400 text-xs ml-2">{{ e.major }} · {{ e.start }} - {{ e.end }}</span>
        </div>
      </Section>
      <Section title="技能">
        <span v-for="s in data.skills" :key="s.name" class="inline-block bg-gray-100 px-2 py-1 rounded text-xs mr-1 mb-1">{{ s.name }}</span>
      </Section>
    </div>

    <!-- Minimal / Tech / English Templates (placeholder for now) -->
    <div v-else class="text-center text-gray-400 py-20">
      预览模板 {{ template }} — 开发中
    </div>
  </div>
</template>

<script setup>
defineProps({ data: Object, template: String })
</script>
