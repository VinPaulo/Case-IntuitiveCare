import { createRouter, createWebHistory } from 'vue-router'
import OperadoraTable from '../components/OperadoraTable.vue'
import OperadoraDetails from '../components/OperadoraDetails.vue'
import DespesasChart from '../components/DespesasChart.vue'

const routes = [
    { path: '/', component: DespesasChart },
    { path: '/operadoras', component: OperadoraTable },
    { path: '/operadoras/:id', component: OperadoraDetails, props: true }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router