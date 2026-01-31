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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg-color: #f8fafc;
  --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  --text-color: #1e293b;
  --text-secondary: #64748b;
  --card-bg: rgba(255, 255, 255, 0.9);
  --card-bg-hover: rgba(255, 255, 255, 0.95);
  --nav-bg: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  --nav-text: #f8fafc;
  --border-color: #e2e8f0;
  --table-header-bg: rgba(241, 245, 249, 0.8);
  --table-row-hover: rgba(248, 250, 252, 0.6);
  --primary-color: #10b981;
  --primary-hover: #059669;
  --accent-color: #3b82f6;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

[data-theme="dark"] {
  --bg-color: #0f172a;
  --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  --text-color: #f1f5f9;
  --text-secondary: #94a3b8;
  --card-bg: rgba(30, 41, 59, 0.8);
  --card-bg-hover: rgba(30, 41, 59, 0.95);
  --nav-bg: linear-gradient(135deg, #020617 0%, #0f172a 100%);
  --nav-text: #f8fafc;
  --border-color: #334155;
  --table-header-bg: rgba(30, 41, 59, 0.6);
  --table-row-hover: rgba(51, 65, 85, 0.4);
  --primary-color: #10b981;
  --primary-hover: #34d399;
  --accent-color: #60a5fa;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-gradient);
  color: var(--text-color);
  margin: 0;
  transition: background 0.3s ease, color 0.3s ease;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  line-height: 1.6;
}

.navbar { 
  background: var(--nav-bg);
  color: var(--nav-text); 
  padding: 1.25rem 1.5rem;
  margin-bottom: 2.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: -0.02em;
  color: var(--nav-text);
}

.container { 
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.links a { 
  color: var(--nav-text);
  text-decoration: none;
  transition: all 0.2s ease;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.95rem;
  position: relative;
}

.links a:hover { 
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.links a.router-link-active { 
  background: rgba(16, 185, 129, 0.15);
  color: var(--primary-color);
  font-weight: 600;
}

.links a.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 2px;
  background: var(--primary-color);
  border-radius: 2px;
}

.theme-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--nav-text);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.theme-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.theme-btn:active {
  transform: translateY(0);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: var(--bg-color);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>