<template>
  <div class="details-container">
    <div v-if="loading && !erro" class="loading-state">
      <p>Carregando informações da operadora...</p>
    </div>

    <div v-if="erro" class="error-state">
      <p>{{ erro }}</p>
      <button @click="$router.back()" class="btn-back">Voltar para a lista</button>
    </div>

    <div v-if="operadora" :key="operadora.registro_ans">
      <div class="header-actions">
        <button @click="$router.back()" class="btn-back">
          <span>←</span> Voltar para a lista
        </button>
      </div>

      <div class="detail-card">
        <div class="card-header">
          <div class="status-badge">Operadora Ativa</div>
          <h1>{{ operadora.razao_social }}</h1>
        </div>
        
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label>Registro ANS</label>
              <p>{{ operadora.registro_ans }}</p>
            </div>
            <div class="info-item">
              <label>CNPJ</label>
              <p>{{ formatCNPJ(operadora.cnpj) }}</p>
            </div>
            <div class="info-item">
              <label>Localização (UF)</label>
              <p><span class="uf-tag">{{ operadora.uf }}</span></p>
            </div>
          </div>
        </div>
      </div>

      <!-- Histórico de Despesas Section -->
      <div class="despesas-section">
        <h3>Histórico de Despesas</h3>
        <p class="section-desc">Detalhamento dos valores reportados por trimestre</p>
        
        <div class="despesas-table-wrapper" v-if="despesas.length > 0">
          <table class="despesas-table">
            <thead>
              <tr>
                <th>Ano</th>
                <th>Trimestre</th>
                <th class="text-right">Valor Despesas</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(d, idx) in despesas" :key="idx">
                <td>{{ d.ano }}</td>
                <td>{{ d.trimestre }}º Trimestre</td>
                <td class="text-right bold">{{ formatMoeda(d.valordespesas) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-despesas">
          <p>Nenhuma despesa processada para esta operadora.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const operadora = ref(null)
const despesas = ref([])
const loading = ref(true)
const erro = ref(null)

const formatCNPJ = (cnpj) => {
  if (!cnpj) return '-'
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2}).*/, "$1.$2.$3/$4-$5")
}

const formatMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor)
}

onMounted(async () => {
  loading.value = true
  try {
    const id = route.params.id
    const [opRes, despRes] = await Promise.all([
      api.get(`/operadoras/${id}`),
      api.get(`/operadoras/${id}/despesas`)
    ])
    operadora.value = opRes.data
    despesas.value = despRes.data
  } catch (error) {
    erro.value = "Não foi possível carregar os detalhes desta operadora. Verifique sua conexão."
    console.error(error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.details-container {
  padding: 24px 0 48px;
  max-width: 1000px;
  margin: 0 auto;
  animation: fadeIn 0.4s ease;
}

.loading-state, .error-state, .empty-despesas {
  text-align: center;
  padding: 80px 0;
  color: var(--text-secondary);
  font-weight: 500;
}

.error-state p { 
  color: #ef4444;
  margin-bottom: 24px;
  font-weight: 600;
}

.header-actions { 
  margin-bottom: 24px;
}

.btn-back {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.btn-back:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-back:active {
  transform: translateY(0);
}

.detail-card {
  background: var(--card-bg);
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 32px;
  backdrop-filter: blur(20px);
  transition: all 0.3s ease;
}

.detail-card:hover {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  padding: 32px 36px;
  background: var(--table-header-bg);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
}

.card-header h1 { 
  margin: 12px 0 0;
  font-size: 1.75rem;
  color: var(--text-color);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.status-badge {
  display: inline-block;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: var(--shadow-sm);
}

.card-body { 
  padding: 36px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 28px;
}

.info-item label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 6px;
  letter-spacing: 0.05em;
}

.info-item p { 
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.uf-tag {
  background: linear-gradient(135deg, var(--table-header-bg) 0%, var(--border-color) 100%);
  color: var(--primary-color);
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}

.despesas-section {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 36px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(20px);
  transition: all 0.3s ease;
}

.despesas-section:hover {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.despesas-section h3 { 
  margin: 0;
  color: var(--text-color);
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.section-desc { 
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin: 6px 0 24px;
  font-weight: 500;
}

.despesas-table-wrapper { 
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.despesas-table { 
  width: 100%;
  border-collapse: collapse;
}

.despesas-table th { 
  background: var(--table-header-bg);
  padding: 14px 24px;
  text-align: left;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.despesas-table td { 
  padding: 14px 24px;
  border-top: 1px solid var(--border-color);
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.despesas-table tbody tr {
  transition: all 0.2s ease;
}

.despesas-table tbody tr:hover { 
  background: var(--table-row-hover);
  transform: scale(1.005);
}

.text-right { 
  text-align: right;
}

.bold { 
  font-weight: 700;
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