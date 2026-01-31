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
  padding: 20px 0 40px;
  max-width: 900px;
  margin: 0 auto;
}

.loading-state, .error-state, .empty-despesas {
  text-align: center;
  padding: 60px 0;
  color: var(--text-color);
  opacity: 0.7;
}

.error-state p { color: #e53e3e; margin-bottom: 20px; }

.header-actions { margin-bottom: 20px; }

.btn-back {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-back:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.detail-card {
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 30px;
}

.card-header {
  padding: 25px 30px;
  background: var(--table-header-bg);
  border-bottom: 1px solid var(--border-color);
}

.card-header h1 { margin: 10px 0 0; font-size: 1.5rem; color: var(--text-color); }

.status-badge {
  display: inline-block;
  background: #e6f7ef;
  color: #2d8a61;
  padding: 4px 10px;
  border-radius: 50px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.card-body { padding: 30px; }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 25px;
}

.info-item label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-color);
  opacity: 0.6;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 5px;
}

.info-item p { font-size: 1.1rem; font-weight: 600; color: var(--text-color); margin: 0; }

.uf-tag {
  background: var(--table-header-bg);
  color: var(--primary-color);
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 700;
  border: 1px solid var(--border-color);
}

.despesas-section {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 30px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.despesas-section h3 { margin: 0; color: var(--text-color); }
.section-desc { font-size: 0.9rem; opacity: 0.7; margin: 5px 0 20px; }

.despesas-table-wrapper { border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; }

.despesas-table { width: 100%; border-collapse: collapse; }
.despesas-table th { background: var(--table-header-bg); padding: 12px 20px; text-align: left; font-size: 0.85rem; font-weight: 600; }
.despesas-table td { padding: 12px 20px; border-top: 1px solid var(--border-color); font-size: 0.95rem; }
.despesas-table tbody tr:hover { background: var(--table-row-hover); }

.text-right { text-align: right; }
.bold { font-weight: 600; }
</style>