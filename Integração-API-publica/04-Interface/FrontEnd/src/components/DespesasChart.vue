<template>
  <div class="card">
    <h2 class="chart-title">Top 5 Crescimento de Despesas (2023-2025)</h2>
    <div class="chart-container">
      <Bar 
        v-if="loaded" 
        :data="chartData" 
        :options="chartOptions" 
        :key="JSON.stringify(chartData)" 
      />
      <div v-else class="loading-state">
        <p>Carregando dados estatísticos...</p>
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
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#2c3e50' }, grid: { color: '#e2e8f0' } },
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
        ticks: { color: textColor }, 
        grid: { color: gridColor } 
      },
      y: { 
        ticks: { color: textColor },
        grid: { display: false } // y axis grid usually looks cleaner hidden for horizontal bars
      }
    }
  }
}

let observer = null

onMounted(async () => {
  // Initial Theme Check
  updateChartTheme()
  
  // Watch for theme changes
  observer = new MutationObserver(updateChartTheme)
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })

  try {
    const response = await api.get('/analise/crescimento')
    const data = response.data
    
    console.log("Dados recebidos da API:", data)

    if (data && data.length > 0) {
      chartData.value = {
        labels: data.map(d => d.razao_social),
        datasets: [{
          label: 'Crescimento %',
          backgroundColor: '#42b983',
          data: data.map(d => d.crescimento)
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
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  margin: 20px;
  border: 1px solid var(--border-color);
}
.chart-title {
  text-align: center;
  color: var(--text-color);
}
.chart-container {
  height: 400px;
  width: 100%;
}
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
}
</style>