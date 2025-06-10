<template>
  <div id="app">
    <div v-if="!liffReady" class="loading-screen">
      <div class="loading-spinner"></div>
      <p>正在初始化...</p>
    </div>
    
    <div v-else class="app-container">
      <NavBar v-if="showNavBar" />
      <main class="main-content">
        <router-view />
      </main>
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: {
    NavBar
  },
  computed: {
    liffReady() {
      return this.$store.state.liffReady
    },
    loading() {
      return this.$store.state.loading
    },
    showNavBar() {
      // 某些頁面不顯示導航欄
      const hideNavRoutes = ['login']
      return !hideNavRoutes.includes(this.$route.name)
    }
  },
  mounted() {
    // 監聽返回鍵
    window.addEventListener('popstate', this.handleBackButton)
  },
  beforeUnmount() {
    window.removeEventListener('popstate', this.handleBackButton)
  },
  methods: {
    handleBackButton() {
      // 處理 LINE 瀏覽器返回鍵
      if (this.$route.path === '/dashboard') {
        this.$liff.closeWindow()
      }
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

#app {
  min-height: 100vh;
}

.loading-screen {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1DB446 0%, #00C851 100%);
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-bottom: 80px; /* 為底部導航留空間 */
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-overlay .loading-spinner {
  margin-bottom: 0;
}

/* 通用樣式 */
.container {
  max-width: 100%;
  margin: 0 auto;
  padding: 16px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
}

.btn-primary {
  background: #1DB446;
  color: white;
}

.btn-primary:hover {
  background: #17a03a;
}

.btn-secondary {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #1DB446;
  box-shadow: 0 0 0 3px rgba(29, 180, 70, 0.1);
}

.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  background: white;
}

.text-center {
  text-align: center;
}

.text-success {
  color: #28a745;
}

.text-danger {
  color: #dc3545;
}

.text-muted {
  color: #6c757d;
}

.mb-2 { margin-bottom: 8px; }
.mb-3 { margin-bottom: 16px; }
.mb-4 { margin-bottom: 24px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 16px; }
.mt-4 { margin-top: 24px; }

.d-flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.align-center {
  align-items: center;
}

.gap-2 {
  gap: 8px;
}

.gap-3 {
  gap: 16px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .container {
    padding: 12px;
  }
  
  .card {
    padding: 16px;
    margin-bottom: 12px;
  }
  
  .btn {
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>