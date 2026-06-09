import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './views/Home.vue'
import Editor from './views/Editor.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/editor/new', component: Editor },
  { path: '/editor/:id', component: Editor },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
