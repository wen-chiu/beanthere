<template>
  <div class="dashboard">
    <div class="container">
      <!-- 用戶歡迎區 -->
      <div class="welcome-card card">
        <div class="d-flex align-center justify-between">
          <div>
            <h2>歡迎回來，{{ user?.name }}！</h2>
            <p class="text-muted">管理你的旅行記帳</p>
          </div>
          <img v-if="user?.picture" :src="user.picture" class="user-avatar" alt="用戶頭像">
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="quick-actions card">
        <h3 class="mb-3">快速操作</h3>
        <div class="action-grid">
          <router-link to="/create-trip" class="action-item">
            <div class="action-icon">🧳</div>
            <span>新增旅行</span>
          </router-link>
          <router-link to="/expense" class="action-item">
            <div class="action-icon">💰</div>
            <span>記帳</span>
          </router-link>
          <router-link to="/expense/ocr" class="action-item">
            <div class="action-icon">📸</div>
            <span>拍照記帳</span>
          </router-link>
          <div @click="showAllTrips" class="action-item">
            <div class="action-icon">📊</div>
            <span>分帳結果</span>
          </div>
        </div>
      </div>

      <!-- 最近的旅行 -->
      <div class="recent-trips card">
        <div class="d-flex justify-between align-center mb-3">
          <h3>最近的旅行</h3>
          <button @click="loadTrips" class="btn btn-secondary">重新整理</button>
        </div>
        
        <div v-if="loading" class="text-center">
          <div class="loading-spinner"></div>
          <p>載入中...</p>
        </div>
        
        <div v-else-if="trips.length === 0" class="empty-state">
          <div class="empty-icon">🧳</div>
          <h4>還沒有任何旅行</h4>
          <p class="text-muted">開始你的第一趟旅程吧！</p>
          <router-link to="/create-trip" class="btn btn-primary mt-3">建立新旅行</router-link>
        </div>
        
        <div v-else class="trip-list">
          <div v-for="trip in trips.slice(0, 3)" :key="trip.id" class="trip-item" @click="goToTrip(trip.id)">
            <div class="trip-info">
              <h4>{{ trip.name }}</h4>
              <p class="text-muted">{{ formatDate(trip.start_date) }} - {{ formatDate(trip.end_date) }}</p>
              <div class="trip-stats">
                <span class="stat-item">👥 {{ trip.member_count }} 人</span>
                <span class="stat-item">💰 {{ $formatCurrency(trip.total_expense) }}</span>
              </div>
            </div>
            <div class="trip-actions">
              <button @click.stop="goToExpense(trip.id)" class="btn btn-secondary btn-sm">記帳</button>
            </div>
          </div>
          
          <div v-if="trips.length > 3" class="show-more">
            <button @click="showAllTrips" class="btn btn-secondary">查看全部 ({{ trips.length }})</button>
          </div>
        </div>
      </div>

      <!-- 統計摘要 -->
      <div class="stats-summary card">
        <h3 class="mb-3">本月統計</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ trips.length }}</div>
            <div class="stat-label">旅行數量</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ $formatCurrency(totalExpenseThisMonth) }}</div>
            <div class="stat-label">總消費</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ totalMembersThisMonth }}</div>
            <div class="stat-label">旅伴數量</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Dashboard',
  data() {
    return {
      loading: false
    }
  },
  computed: {
    ...mapState(['user']),
    ...mapState('trips', ['trips']),
    totalExpenseThisMonth() {
      const currentMonth = new Date().getMonth()
      const currentYear = new Date().getFullYear()
      
      return this.trips
        .filter(trip => {
          const tripDate = new Date(trip.start_date)
          return tripDate.getMonth() === currentMonth && tripDate.getFullYear() === currentYear
        })
        .reduce((sum, trip) => sum + (trip.total_expense || 0), 0)
    },
    totalMembersThisMonth() {
      const currentMonth = new Date().getMonth()
      const currentYear = new Date().getFullYear()
      
      return this.trips
        .filter(trip => {
          const tripDate = new Date(trip.start_date)
          return tripDate.getMonth() === currentMonth && tripDate.getFullYear() === currentYear
        })
        .reduce((sum, trip) => sum + (trip.member_count || 0), 0)
    }
  },
  created() {
    this.loadTrips()
  },
  methods: {
    ...mapActions('trips', ['fetchTrips']),
    async loadTrips() {
      if (!this.user) return
      
      this.loading = true
      try {
        await this.fetchTrips(this.user.id)
      } catch (error) {
        console.error('載入旅行列表失敗:', error)
        this.$liff.sendMessages([{
          type: 'text',
          text: '載入資料失敗，請稍後再試'
        }])
      } finally {
        this.loading = false
      }
    },
    goToTrip(tripId) {
      this.$router.push(`/trip/${tripId}`)
    },
    goToExpense(tripId) {
      this.$router.push(`/expense?trip_id=${tripId}`)
    },
    showAllTrips() {
      this.$router.push('/trips')
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-TW', {
        month: 'short',
        day: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px 0;
  background: linear-gradient(135deg, #1DB446 0%, #00C851 100%);
  min-height: 100vh;
}

.welcome-card {
  background: white;
  margin-bottom: 20px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.quick-actions {
  margin-bottom: 20px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  text-decoration: none;
  color: #333;
  transition: all 0.2s ease;
  cursor: pointer;
}

.action-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.trip-list {
  space-y: 12px;
}

.trip-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
  margin-bottom: 12px;
}

.trip-item:hover {
  background: #e9ecef;
}

.trip-info h4 {
  margin-bottom: 4px;
  color: #333;
}

.trip-stats {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.stat-item {
  font-size: 14px;
  color: #666;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #1DB446;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.show-more {
  text-align: center;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .action-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .trip-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>