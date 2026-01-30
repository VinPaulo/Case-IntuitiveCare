import { defineStore } from 'pinia'
import api from '../services/api'

export const useOperadoraStore = defineStore('operadora', {
    state: () => ({
        operadoras: [],
        loading: false
    }),
    actions: {
        async fetchOperadoras() {
            this.loading = true
            try {
                const response = await api.get('/operadoras')
                this.operadoras = response.data.data
            } finally {
                this.loading = false
            }
        }
    }
})