<template>
  <div class="table-container">
    <div class="table-header">
      <div class="header-main">
        <div>
          <h2>Operadoras Cadastradas</h2>
          <p>Gerenciamento e visualização das operadoras ativas na ANS</p>
        </div>
        <div class="search-box">
          <input 
            v-model="search" 
            @input="handleSearch" 
            type="text" 
            placeholder="Buscar por nome, CNPJ ou Registro..."
          >
        </div>
      </div>
    </div>
    
    <div class="table-wrapper">
      <table class="styled-table">
        <thead>
          <tr>
            <th>Registro ANS</th>
            <th>Razão Social</th>
            <th>CNPJ</th>
            <th>UF</th>
            <th class="text-center">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="no-hover">
            <td colspan="5" class="text-center">Carregando dados...</td>
          </tr>
          <tr v-else-if="operadoras.length === 0" class="no-hover">
            <td colspan="5" class="text-center">Nenhuma operadora encontrada.</td>
          </tr>
          <tr v-for="op in operadoras" :key="op.registro_ans">
            <td><span class="badge">{{ op.registro_ans }}</span></td>
            <td class="bold">{{ op.razao_social }}</td>
            <td>{{ formatCNPJ(op.cnpj) }}</td>
            <td><span class="uf-tag">{{ op.uf }}</span></td>
            <td class="text-center">
              <button @click="$router.push('/operadoras/' + op.registro_ans)" class="btn-detail">
                Ver Detalhes
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="table-footer">
      <div class="pagination-info">
        Mostrando {{ operadoras.length }} de {{ total }} registros
      </div>
      <div class="pagination-controls">
        <button :disabled="page === 1" @click="changePage(-1)" class="btn-page">Anterior</button>
        <span class="page-indicator">Página {{ page }} de {{ totalPages }}</span>
        <button :disabled="page >= totalPages" @click="changePage(1)" class="btn-page">Próximo</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

const operadoras = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const search = ref('')
const loading = ref(false)

const totalPages = computed(() => Math.ceil(total.value / limit.value) || 1)

const formatCNPJ = (cnpj) => {
  if (!cnpj) return '-'
  const c = cnpj.replace(/\D/g, '')
  return c.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2}).*/, "$1.$2.$3/$4-$5")
}

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/operadoras', {
      params: { page: page.value, limit: limit.value, search: search.value }
    })
    operadoras.value = data.data
    total.value = data.total
  } catch (e) {
    console.error("Erro ao carregar operadoras", e)
  } finally {
    loading.value = false
  }
}

let searchTimeout = null
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadData()
  }, 500)
}

const changePage = (delta) => {
  page.value += delta
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.table-container {
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-top: 20px;
  border: 1px solid var(--border-color);
}

.table-header {
  padding: 20px 25px;
  background: var(--table-header-bg);
  border-bottom: 1px solid var(--border-color);
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.search-box input {
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  color: var(--text-color);
  min-width: 300px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: var(--primary-color);
}

.table-header h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.5rem;
}

.table-header p {
  margin: 5px 0 0;
  color: var(--text-color);
  opacity: 0.7;
  font-size: 0.9rem;
}

.table-wrapper {
  overflow-x: auto;
  min-height: 200px;
}

.styled-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.styled-table thead tr {
  background-color: var(--table-header-bg);
  color: var(--text-color);
  text-align: left;
  font-weight: 600;
}

.styled-table th, .styled-table td {
  padding: 15px 25px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
}

.styled-table tbody tr:hover:not(.no-hover) {
  background-color: var(--table-row-hover);
  transition: background 0.2s;
}

.table-footer {
  padding: 15px 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--table-header-bg);
  border-top: 1px solid var(--border-color);
}

.pagination-info {
  font-size: 0.85rem;
  color: var(--text-color);
  opacity: 0.8;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.btn-page {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-page:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.9rem;
  font-weight: 500;
}

.bold { font-weight: 600; }

.badge {
  background: #e0f2fe;
  color: #0369a1;
  padding: 4px 8px;
  border-radius: 6px;
  font-family: monospace;
  font-weight: bold;
}

.uf-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: bold;
}

.btn-detail {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: opacity 0.2s;
}

.btn-detail:hover { opacity: 0.85; }
.text-center { text-align: center; }
</style>