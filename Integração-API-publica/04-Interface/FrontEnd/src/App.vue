<template>
  <div id="app">
    <nav class="navbar">
      <div class="container" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
        <span class="logo">Case Intuitive Care - ANS Dashboard</span>
        <div class="links" style="display: flex; align-items: center;">
          <router-link to="/">Gráfico de Crescimento</router-link>
          <router-link to="/operadoras">Lista de Operadoras</router-link>
          <button @click="toggleTheme" class="theme-btn">
            {{ isDark ? 'Claro' : 'Escuro' }}
          </button>
        </div>
      </div>
    </nav>
    <main class="container">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const isDark = ref(false)

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved) {
    isDark.value = saved === 'dark'
    document.documentElement.setAttribute('data-theme', saved)
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<style>
:root {
  --bg-color: #f4f7f6;
  --text-color: #2c3e50;
  --card-bg: #ffffff;
  --nav-bg: #2c3e50;
  --nav-text: #ffffff;
  --border-color: #e2e8f0;
  --table-header-bg: #f1f5f9;
  --table-row-hover: #f8fafc;
  --primary-color: #42b983;
}

[data-theme="dark"] {
  --bg-color: #1a202c;
  --text-color: #e2e8f0;
  --card-bg: #2d3748;
  --nav-bg: #171923;
  --nav-text: #e2e8f0;
  --border-color: #4a5568;
  --table-header-bg: #2d3748;
  --table-row-hover: #2d3748;
  --primary-color: #42b983;
}

body {
  font-family: 'Inter', Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  margin: 0;
  transition: background-color 0.3s, color 0.3s;
}

.navbar { 
  background: var(--nav-bg); 
  color: var(--nav-text); 
  padding: 1rem; 
  margin-bottom: 2rem; 
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.container { max-width: 1000px; margin: 0 auto; padding: 0 10px; }
.links a { color: var(--nav-text); margin-left: 20px; text-decoration: none; transition: opacity 0.2s; }
.links a:hover { opacity: 0.8; }
.links a.router-link-active { font-weight: bold; border-bottom: 2px solid var(--primary-color); }

.theme-btn {
  background: none;
  border: 1px solid var(--nav-text);
  color: var(--nav-text);
  padding: 5px 12px;
  border-radius: 20px;
  cursor: pointer;
  margin-left: 20px;
  font-size: 0.85rem;
}

.theme-btn:hover {
  background: rgba(255,255,255,0.1);
}
</style>