<template>
  <div class="details-container">
    <div v-if="!operadora && !erro" class="loading-state">
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
              <p>{{ operadora.cnpj }}</p>
            </div>
            <div class="info-item">
              <label>Localização (UF)</label>
              <p><span class="uf-tag">{{ operadora.uf }}</span></p>
            </div>
          </div>
        </div>
        
        <div class="card-footer">
          <p>Dados extraídos da base oficial da ANS (Agência Nacional de Saúde Suplementar).</p>
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
const erro = ref(null)

onMounted(async () => {
  try {
    const id = route.params.id
    const response = await api.get(`/operadoras/${id}`)
    operadora.value = response.data
  } catch (error) {
    erro.value = "Não foi possível carregar os detalhes desta operadora. Verifique sua conexão."
    console.error(error)
  }
})
</script>

<style scoped>
.details-container {
  padding: 40px 20px;
  max-width: 900px;
  margin: 0 auto;
  font-family: sans-serif;
}

.loading-state, .error-state {
  text-align: center;
  padding: 100px 0;
  color: var(--text-color);
  opacity: 0.7;
}

.error-state p {
  color: #e53e3e;
  margin-bottom: 20px;
}

.header-actions {
  margin-bottom: 25px;
}

.btn-back {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-color);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-back:hover {
  background: var(--table-header-bg);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.detail-card {
  background: var(--card-bg);
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.08);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.card-header {
  padding: 40px;
  background: var(--table-header-bg);
  border-bottom: 1px solid var(--border-color);
}

.card-header h1 {
  margin: 15px 0 0;
  font-size: 2rem;
  color: var(--text-color);
}

.status-badge {
  display: inline-block;
  background: #e6f7ef;
  color: #2d8a61;
  padding: 6px 14px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.card-body {
  padding: 40px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 40px;
}

.info-item label {
  display: block;
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.6;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 8px;
}

.info-item p {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.uf-tag {
  display: inline-block;
  background: var(--table-row-hover);
  color: #4f46e5;
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  border: 1px solid var(--border-color);
}

.card-footer {
  background: var(--table-header-bg);
  padding: 20px 40px;
  border-top: 1px solid var(--border-color);
}

.card-footer p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-color);
  opacity: 0.7;
}
</style>