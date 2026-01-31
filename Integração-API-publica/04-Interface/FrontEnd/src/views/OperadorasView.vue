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
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  margin-top: 24px;
  border: 1px solid var(--border-color);
  backdrop-filter: blur(20px);
  animation: fadeIn 0.4s ease;
  transition: all 0.3s ease;
}

.table-container:hover {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.table-header {
  padding: 28px 32px;
  background: var(--table-header-bg);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.search-box input {
  padding: 12px 18px;
  border-radius: 10px;
  border: 2px solid var(--border-color);
  background: var(--card-bg);
  color: var(--text-color);
  min-width: 320px;
  outline: none;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  font-weight: 500;
}

.search-box input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
  transform: translateY(-1px);
}

.search-box input::placeholder {
  color: var(--text-secondary);
  font-weight: 400;
}

.table-header h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.table-header p {
  margin: 6px 0 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 500;
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
  padding: 18px 32px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
  transition: all 0.2s ease;
}

.styled-table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.styled-table tbody tr {
  transition: all 0.2s ease;
}

.styled-table tbody tr:hover:not(.no-hover) {
  background-color: var(--table-row-hover);
  transform: scale(1.01);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.table-footer {
  padding: 20px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--table-header-bg);
  border-top: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
}

.pagination-info {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-page {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  color: var(--text-color);
  padding: 8px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-page:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-page:active:not(:disabled) {
  transform: translateY(0);
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-color);
}

.bold { 
  font-weight: 600;
}

.badge {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  padding: 6px 12px;
  border-radius: 8px;
  font-family: 'Inter', monospace;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 0.02em;
  box-shadow: var(--shadow-sm);
}

.uf-tag {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #475569;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-sm);
}

.btn-detail {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-md);
}

.btn-detail:hover { 
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-detail:active {
  transform: translateY(0);
}

.text-center { 
  text-align: center;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
