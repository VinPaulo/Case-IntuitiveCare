<template>
  <div class="table-container">
    <div class="table-header">
      <h2>Operadoras Cadastradas</h2>
      <p>Gerenciamento e visualização das operadoras ativas na ANS</p>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const operadoras = ref([])

const formatCNPJ = (cnpj) => {
  return cnpj.replace(/^(\dt{2})(\dt{3})(\dt{3})(\dt{4})(\dt{2}).*/, "$1.$2.$3/$4-$5")
}

onMounted(async () => {
  try {
    const { data } = await api.get('/operadoras')
    operadoras.value = data.data
  } catch (e) {
    console.error("Erro ao carregar operadoras", e)
  }
})
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

.styled-table tbody tr:hover {
  background-color: var(--table-row-hover);
  transition: background 0.2s;
}

.bold { font-weight: 600; color: #1e293b; }

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

.btn-detail:hover {
  opacity: 0.85;
}

.text-center { text-align: center; }
</style>