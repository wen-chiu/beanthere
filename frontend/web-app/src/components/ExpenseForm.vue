// ExpenseForm.vue
<template>
  <div class="expense-form">
    <div class="container">
      <div class="card">
        <h2 class="mb-4">{{ isOCR ? '拍照記帳' : '手動記帳' }}</h2>
        
        <!-- 旅行選擇 -->
        <div class="form-group">
          <label class="form-label">選擇旅行</label>
          <select v-model="selectedTripId" class="form-select" required>
            <option value="">請選擇旅行</option>
            <option v-for="trip in trips" :key="trip.id" :value="trip.id">
              {{ trip.name }}
            </option>
          </select>
        </div>
        
        <!-- OCR 上傳區域 -->
        <div v-if="isOCR" class="ocr-upload-area">
          <div class="upload-zone" @click="triggerFileUpload" @dragover.prevent @drop="handleDrop">
            <input ref="fileInput" type="file" accept="image/*" @change="handleFileUpload" style="display: none">
            <div v-if="!uploadedImage" class="upload-placeholder">
              <div class="upload-icon">📸</div>
              <p>點擊或拖拽上傳收據照片</p>
              <small class="text-muted">支援 JPG、PNG 格式</small>
            </div>
            <div v-else class="uploaded-image">
              <img :src="uploadedImage" alt="上傳的收據" />
              <button @click.stop="removeImage" class="remove-btn">✕</button>
            </div>
          </div>
          
          <div v-if="ocrProcessing" class="ocr-processing">
            <div class="loading-spinner"></div>
            <p>AI 正在辨識收據內容...</p>
          </div>
        </div>
        
        <!-- 記帳表單 -->
        <form @submit.prevent="submitExpense">
          <div class="form-group">
            <label class="form-label">消費項目</label>
            <input v-model="expenseData.description" type="text" class="form-input" placeholder="例如：午餐、住宿費" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">金額</label>
            <input v-model.number="expenseData.amount" type="number" class="form-input" placeholder="0" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">消費分類</label>
            <select v-model="expenseData.category" class="form-select" required>
              <option value="">請選擇分類</option>
              <option value="food">🍽️ 餐飲</option>
              <option value="accommodation">🏨 住宿</option>
              <option value="transportation">🚗 交通</option>
              <option value="entertainment">🎡 娛樂</option>
              <option value="shopping">🛍️ 購物</option>
              <option value="other">📦 其他</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">付款人</label>
            <select v-model="expenseData.payerId" class="form-select" required>
              <option value="">請選擇付款人</option>
              <option v-for="member in currentTripMembers" :key="member.id" :value="member.id">
                {{ member.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">參與分帳的成員</label>
            <div class="member-selection">
              <div v-for="member in currentTripMembers" :key="member.id" class="member-checkbox">
                <input 
                  :id="`member-${member.id}`"
                  v-model="expenseData.participants" 
                  :value="member.id" 
                  type="checkbox"
                  class="checkbox-input"
                >
                <label :for="`member-${member.id}`" class="checkbox-label">
                  {{ member.name }}
                </label>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">備註 (可選)</label>
            <textarea v-model="expenseData.note" class="form-input" rows="3" placeholder="其他說明..."></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="goBack" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? '儲存中...' : '儲存記帳' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'ExpenseForm',
  props: {
    isOCR: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      selectedTripId: '',
      uploadedImage: null,
      ocrProcessing: false,
      submitting: false,
      expenseData: {
        description: '',
        amount: 0,
        category: '',
        payerId: '',
        participants: [],
        note: ''
      }
    }
  },
  computed: {
    ...mapState('trips', ['trips']),
    ...mapState('expenses', ['expenses']),
    currentTripMembers() {
      if (!this.selectedTripId) return []
      const trip = this.trips.find(t => t.id === this.selectedTripId)
      return trip ? trip.members : []
    }
  },
  created() {
    this.loadTrips()
    // 從 query 參數獲取 trip_id
    if (this.$route.query.trip_id) {
      this.selectedTripId = this.$route.query.trip_id
    }
  },
  methods: {
    ...mapActions('trips', ['fetchTrips']),
    ...mapActions('expenses', ['createExpense']),
    async loadTrips() {
      if (!this.$store.state.user) return
      try {
        await this.fetchTrips(this.$store.state.user.id)
      } catch (error) {
        console.error('載入旅行列表失敗:', error)
      }
    },
    triggerFileUpload() {
      this.$refs.fileInput.click()
    },
    handleFileUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.processImage(file)
      }
    },
    handleDrop(event) {
      event.preventDefault()
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        this.processImage(file)
      }
    },
    async processImage(file) {
      // 顯示預覽圖片
      const reader = new FileReader()
      reader.onload = (e) => {
        this.uploadedImage = e.target.result
      }
      reader.readAsDataURL(file)
      
      // 開始 OCR 處理
      if (this.isOCR) {
        await this.processOCR(file)
      }
    },
    async processOCR(file) {
      this.ocrProcessing = true
      
      try {
        const formData = new FormData()
        formData.append('image', file)
        
        const response = await fetch('/api/v1/ocr/process', {
          method: 'POST',
          body: formData
        })
        
        const result = await response.json()
        
        if (result.success) {
          // 自動填入 OCR 辨識結果
          this.expenseData.description = result.data.description || ''
          this.expenseData.amount = result.data.amount || 0
          this.expenseData.category = result.data.category || ''
        }
      } catch (error) {
        console.error('OCR 處理失敗:', error)
      } finally {
        this.ocrProcessing = false
      }
    },
    removeImage() {
      this.uploadedImage = null
      this.$refs.fileInput.value = ''
    },
    async submitExpense() {
      if (!this.selectedTripId || !this.expenseData.description || !this.expenseData.amount) {
        alert('請填寫必要資訊')
        return
      }
      
      this.submitting = true
      
      try {
        const expensePayload = {
          tripId: this.selectedTripId,
          ...this.expenseData,
          createdBy: this.$store.state.user.id
        }
        
        await this.createExpense(expensePayload)
        
        // 發送成功訊息到 LINE
        this.$liff.sendMessages([{
          type: 'text',
          text: `✅ 記帳成功！\n\n項目：${this.expenseData.description}\n金額：NT$ ${this.expenseData.amount.toLocaleString()}`
        }])
        
        // 返回上一頁或關閉視窗
        this.goBack()
      } catch (error) {
        console.error('記帳失敗:', error)
        alert('記帳失敗，請稍後再試')
      } finally {
        this.submitting = false
      }
    },
    goBack() {
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        this.$liff.closeWindow()
      }
    }
  }
}
</script>

<style scoped>
.expense-form {
  padding: 20px 0;
  min-height: 100vh;
  background: #f5f5f5;
}

.ocr-upload-area {
  margin-bottom: 24px;
}

.upload-zone {
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease;
  position: relative;
}

.upload-zone:hover {
  border-color: #1DB446;
}

.upload-placeholder .upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.uploaded-image {
  position: relative;
  display: inline-block;
}

.uploaded-image img {
  max-width: 
}