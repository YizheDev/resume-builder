import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import Home from './views/Home.vue'
import ChatView from './views/ChatView.vue'
import EditorView from './views/EditorView.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/chat/:id', component: ChatView },
  { path: '/edit/:id', component: EditorView },
]

const router = createRouter({ history: createWebHistory(), routes })
const pinia = createPinia()

createApp(App).use(router).use(pinia).mount('#app')
