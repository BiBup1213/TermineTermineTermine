import { createRouter, createWebHistory } from 'vue-router'
import CreatePollPage from '../pages/CreatePollPage.vue'
import PollPage from '../pages/PollPage.vue'
import ResultsPage from '../pages/ResultsPage.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: CreatePollPage },
    { path: '/p/:pollId', component: PollPage },
    { path: '/p/:pollId/results', component: ResultsPage }
  ]
})
