import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/agent/new',
    name: 'AgentNew',
    component: () => import('@/views/Agent/AgentEditor.vue')
  },
  {
    path: '/agent/:id/edit',
    name: 'AgentEdit',
    component: () => import('@/views/Agent/AgentEditor.vue'),
    props: true
  },
  {
    path: '/workflow/:id/edit',
    name: 'WorkflowEdit',
    component: () => import('@/views/Workflow/WorkflowEditor.vue'),
    props: true
  },
  {
    path: '/plugins/:id',
    name: 'PluginDetail',
    component: () => import('@/views/Plugin/PluginDetail.vue'),
    props: true
  },
  {
    path: '/knowledge',
    name: 'KnowledgeBaseList',
    component: () => import('@/views/Knowledge/KnowledgeBaseList.vue')
  },
  {
    path: '/knowledge/:id',
    name: 'KnowledgeBaseDetail',
    component: () => import('@/views/Knowledge/KnowledgeBaseDetail.vue'),
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

