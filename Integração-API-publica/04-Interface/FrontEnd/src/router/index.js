import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import OperadorasView from '../views/OperadorasView.vue'
import OperadoraDetailView from '../views/OperadoraDetailView.vue'

const routes = [
    { path: '/', component: HomeView },
    { path: '/operadoras', component: OperadorasView },
    { path: '/operadoras/:id', component: OperadoraDetailView, props: true }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router