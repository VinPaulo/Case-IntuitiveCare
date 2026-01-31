<template>
  <div class="card">
    <div class="card-header">
      <h2 class="chart-title">Distribuição de Despesas por UF</h2>
      <p class="chart-subtitle">Estados com maior volume de gastos registrados</p>
    </div>
    <div class="chart-container">
      <Bar 
        v-if="loaded" 
        :data="chartData" 
        :options="chartOptions" 
        :key="JSON.stringify(chartData)" 
      />
      <div v-else class="loading-state">
        <div class="spinner"></div>
        <p>Carregando dados geográficos...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { 
  Chart as ChartJS, Title, Tooltip, Legend, 
  BarElement, CategoryScale, LinearScale 
} from 'chart.js'
import api from '../services/api'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const loaded = ref(false)
const chartData = ref({ labels: [], datasets: [] })
const chartOptions = ref({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (context) => {
          let label = context.dataset.label || ''
          if (label) label += ': '
          if (context.parsed.x !== null) {
            label += new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.parsed.x)
          }
          return label
        }
      }
    }
  },
  scales: {
    x: { 
      ticks: { 
        color: '#2c3e50',
        callback: (value) => {
          if (value >= 1e9) return (value / 1e9).toFixed(1) + ' bi'
          if (value >= 1e6) return (value / 1e6).toFixed(1) + ' mi'
          return value
        }
      }, 
      grid: { color: '#e2e8f0' } 
    },
    y: { ticks: { color: '#2c3e50' }, grid: { display: false } }
  }
})

const updateChartTheme = () => {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
  const textColor = isDark ? '#e2e8f0' : '#2c3e50'
  const gridColor = isDark ? '#4a5568' : '#e2e8f0'

  chartOptions.value = {
    ...chartOptions.value,
    scales: {
      x: { 
        ...chartOptions.value.scales.x,
        ticks: { ...chartOptions.value.scales.x.ticks, color: textColor }, 
        grid: { color: gridColor } 
      },
      y: { 
        ...chartOptions.value.scales.y,
        ticks: { ...chartOptions.value.scales.y.ticks, color: textColor },
        grid: { display: false } 
      }
    }
  }
}

let observer = null

onMounted(async () => {
  updateChartTheme()

  observer = new MutationObserver(updateChartTheme)
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })

  try {
    const response = await api.get('/analise/despesas-por-uf')
    const data = response.data
    
    if (data && data.length > 0) {
      chartData.value = {
        labels: data.map(d => d.uf),
        datasets: [{
          label: 'Total de Despesas',
          backgroundColor: '#42b983',
          borderRadius: 6,
          data: data.map(d => d.total_despesa)
        }]
      }
    }
    loaded.value = true
  } catch (error) {
    console.error("Erro na requisição do gráfico:", error)
    loaded.value = true
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.card {
  background: var(--card-bg);
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  margin-top: 20px;
  border: 1px solid var(--border-color);
}
.card-header { text-align: center; margin-bottom: 25px; }
.chart-title { margin: 0; color: var(--text-color); font-size: 1.5rem; }
.chart-subtitle { margin: 5px 0 0; color: var(--text-color); opacity: 0.6; font-size: 0.9rem; }

.chart-container {
  height: 450px;
  width: 100%;
}
.loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
  gap: 15px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(66, 185, 131, 0.1);
  border-left-color: #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>