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
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
          hoverBackgroundColor: 'rgba(16, 185, 129, 1)',
          borderRadius: 8,
          borderSkipped: false,
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
  padding: 36px;
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  margin-top: 24px;
  border: 1px solid var(--border-color);
  backdrop-filter: blur(20px);
  animation: fadeIn 0.4s ease;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header { 
  text-align: center;
  margin-bottom: 32px;
}

.chart-title { 
  margin: 0;
  color: var(--text-color);
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.chart-subtitle { 
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 500;
}

.chart-container {
  height: 500px;
  width: 100%;
  position: relative;
}

.loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-secondary);
  gap: 20px;
  font-weight: 500;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(16, 185, 129, 0.1);
  border-left-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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