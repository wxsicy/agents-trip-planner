<template>
  <div class="home-container">
    <!-- Hero 区域 -->
    <div class="hero-section">
      <!-- 装饰性 SVG 元素 -->
      <svg class="deco-plane" width="64" height="64" viewBox="0 0 24 24" fill="none">
        <path d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" fill="rgba(255,255,255,0.15)"/>
      </svg>
      <svg class="deco-compass" width="56" height="56" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.12)" stroke-width="1.5"/>
        <polygon points="12,2 14,10 12,8 10,10" fill="rgba(255,255,255,0.2)"/>
        <polygon points="12,22 10,14 12,16 14,14" fill="rgba(255,255,255,0.12)"/>
      </svg>
      <svg class="deco-pin" width="44" height="44" viewBox="0 0 24 24" fill="none">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="rgba(255,255,255,0.1)"/>
        <circle cx="12" cy="9" r="2.5" fill="rgba(255,255,255,0.15)"/>
      </svg>

      <div class="hero-content">
        <div class="hero-badge">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
          Multi-Agent Trip Planner
        </div>
        <h1 class="hero-title">智能旅行助手</h1>
        <p class="hero-subtitle">
          基于多智能体协作，为你量身定制完美旅程<br/>
          景点推荐 · 天气预测 · 酒店筛选 · 行程规划，一站搞定
        </p>
      </div>

      <!-- 底部波浪 -->
      <div class="hero-wave">
        <svg viewBox="0 0 1440 120" preserveAspectRatio="none">
          <path d="M0,40 C360,100 720,0 1080,60 C1260,90 1380,30 1440,50 L1440,120 L0,120 Z" fill="#f0f2f5"/>
        </svg>
      </div>
    </div>

    <!-- 特色卡片 -->
    <div class="features-row">
      <div class="feature-card" v-for="f in features" :key="f.icon">
        <div class="feature-icon" :style="{ background: f.bg }">{{ f.icon }}</div>
        <div class="feature-text">
          <div class="feature-title">{{ f.title }}</div>
          <div class="feature-desc">{{ f.desc }}</div>
        </div>
      </div>
    </div>

    <!-- 表单区域 -->
    <div class="form-wrapper">
      <!-- 目的地与日期 -->
      <div class="form-section">
        <div class="section-header">
          <div class="section-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5S13.38 11.5 12 11.5z"/></svg>
          </div>
          <div>
            <div class="section-title">目的地与日期</div>
            <div class="section-hint">告诉我们你想去哪里、什么时候出发</div>
          </div>
        </div>
        <a-row :gutter="16">
          <a-col :span="8">
            <label class="field-label">目的地城市</label>
            <a-input v-model:value="formData.city" placeholder="如：北京、上海、杭州" size="large">
              <template #prefix><span style="color:#bfbfbf">&#127961;</span></template>
            </a-input>
          </a-col>
          <a-col :span="5">
            <label class="field-label">开始日期</label>
            <a-date-picker v-model:value="startDatePicker" style="width: 100%" size="large" placeholder="选择出发日" />
          </a-col>
          <a-col :span="5">
            <label class="field-label">结束日期</label>
            <a-date-picker v-model:value="endDatePicker" style="width: 100%" size="large" placeholder="选择返程日" />
          </a-col>
          <a-col :span="3">
            <label class="field-label">人数</label>
            <a-input-number v-model:value="formData.people_count" :min="1" :max="20" style="width: 100%" size="large" />
          </a-col>
          <a-col :span="3">
            <label class="field-label">天数</label>
            <a-input-number v-model:value="formData.days" :min="1" :max="30" style="width: 100%" size="large" />
          </a-col>
        </a-row>
      </div>

      <!-- 偏好设置 -->
      <div class="form-section">
        <div class="section-header">
          <div class="section-icon" style="background: linear-gradient(135deg, #f093fb, #f5576c);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          </div>
          <div>
            <div class="section-title">偏好设置</div>
            <div class="section-hint">个性化你的旅行风格</div>
          </div>
        </div>
        <a-row :gutter="16">
          <a-col :span="6">
            <label class="field-label">节奏偏好</label>
            <a-select v-model:value="formData.pace" size="large" style="width: 100%">
              <a-select-option value="轻松">🐢 轻松休闲</a-select-option>
              <a-select-option value="适中">🚶 适中节奏</a-select-option>
              <a-select-option value="紧凑">🏃 紧凑打卡</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="6">
            <label class="field-label">住宿偏好</label>
            <a-select v-model:value="formData.accommodation" size="large" style="width: 100%">
              <a-select-option value="经济型">🏨 经济型</a-select-option>
              <a-select-option value="舒适型">🏩 舒适型</a-select-option>
              <a-select-option value="豪华型">🏰 豪华型</a-select-option>
              <a-select-option value="民宿">🏡 特色民宿</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="12">
            <label class="field-label">预算（元/人）</label>
            <a-input v-model:value="formData.budget" placeholder="如：3000" size="large">
              <template #prefix><span style="color:#bfbfbf">¥</span></template>
            </a-input>
          </a-col>
        </a-row>

        <div style="margin-top: 20px;">
          <label class="field-label">旅行偏好</label>
          <div class="tag-group">
            <div
              v-for="opt in preferenceOptions"
              :key="opt.value"
              class="tag-item"
              :class="{ active: formData.preferences.includes(opt.value) }"
              @click="togglePreference(opt.value)"
            >
              <span class="tag-icon">{{ opt.icon }}</span>
              {{ opt.label }}
            </div>
          </div>
        </div>

        <div style="margin-top: 20px;">
          <label class="field-label">饮食偏好</label>
          <div class="tag-group">
            <div
              v-for="opt in foodOptions"
              :key="opt.value"
              class="tag-item"
              :class="{ active: formData.food_preferences.includes(opt.value) }"
              @click="toggleFood(opt.value)"
            >
              <span class="tag-icon">{{ opt.icon }}</span>
              {{ opt.label }}
            </div>
          </div>
        </div>
      </div>

      <!-- 额外要求 -->
      <div class="form-section">
        <div class="section-header">
          <div class="section-icon" style="background: linear-gradient(135deg, #4facfe, #00f2fe);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>
          </div>
          <div>
            <div class="section-title">额外要求</div>
            <div class="section-hint">任何特殊需求都可以告诉我们</div>
          </div>
        </div>
        <a-textarea
          v-model:value="formData.extra_requirements"
          placeholder="例如：不想太早起床、希望安排一个看日落的地点、有老人同行需要无障碍设施..."
          :rows="3"
          size="large"
        />
      </div>

      <!-- 提交按钮 -->
      <div class="submit-section">
        <a-button
          type="primary"
          html-type="submit"
          size="large"
          :loading="loading"
          block
          class="submit-btn"
          @click="handleSubmit"
        >
          <svg v-if="!loading" width="20" height="20" viewBox="0 0 24 24" fill="white" style="margin-right: 8px;">
            <path d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
          </svg>
          {{ loading ? '正在规划中...' : '开始规划我的旅程' }}
        </a-button>

        <div v-if="loading" class="loading-section">
          <a-progress :percent="loadingProgress" status="active" :stroke-color="{ from: '#667eea', to: '#764ba2' }" />
          <p class="loading-status">{{ loadingStatus }}</p>
        </div>
      </div>
    </div>

    <!-- 底部 -->
    <footer class="page-footer">
      <p>Powered by Multi-Agent System · 高德地图 · Unsplash · LLM</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { generateTripPlan } from '@/services/api'

const router = useRouter()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')
const startDatePicker = ref<any>(null)
const endDatePicker = ref<any>(null)

const features = [
  { icon: '🔍', title: '智能景点推荐', desc: '基于高德地图实时搜索', bg: 'linear-gradient(135deg, #667eea22, #764ba222)' },
  { icon: '🌤️', title: '天气智能预测', desc: '提前了解目的地天气', bg: 'linear-gradient(135deg, #4facfe22, #00f2fe22)' },
  { icon: '🏨', title: '酒店精准匹配', desc: '按预算与偏好筛选', bg: 'linear-gradient(135deg, #f093fb22, #f5576c22)' },
  { icon: '📋', title: '行程一键生成', desc: '多智能体协作规划', bg: 'linear-gradient(135deg, #43e97b22, #38f9d722)' },
]

const preferenceOptions = [
  { label: '自然风景', value: '自然风景', icon: '🏔️' },
  { label: '拍照打卡', value: '拍照', icon: '📸' },
  { label: '美食探店', value: '美食', icon: '🍜' },
  { label: '古镇漫步', value: '古镇', icon: '🏘️' },
  { label: '休闲放松', value: '休闲', icon: '🧘' },
  { label: '历史文化', value: '历史文化', icon: '🏛️' },
  { label: '购物血拼', value: '购物', icon: '🛍️' },
  { label: '亲子出游', value: '亲子', icon: '👨‍👩‍👧' },
]

const foodOptions = [
  { label: '少辣', value: '少辣', icon: '🌶️' },
  { label: '不吃香菜', value: '不吃香菜', icon: '🌿' },
  { label: '不吃葱', value: '不吃葱', icon: '🧅' },
  { label: '素食', value: '素食', icon: '🥬' },
  { label: '清真', value: '清真', icon: '🍽️' },
]

const togglePreference = (val: string) => {
  const idx = formData.value.preferences.indexOf(val)
  if (idx >= 0) formData.value.preferences.splice(idx, 1)
  else formData.value.preferences.push(val)
}

const toggleFood = (val: string) => {
  const idx = formData.value.food_preferences.indexOf(val)
  if (idx >= 0) formData.value.food_preferences.splice(idx, 1)
  else formData.value.food_preferences.push(val)
}

watch([startDatePicker, endDatePicker], () => {
  if (startDatePicker.value && endDatePicker.value) {
    const start = dayjs(startDatePicker.value)
    const end = dayjs(endDatePicker.value)
    const diff = end.diff(start, 'day') + 1
    if (diff > 0) {
      formData.value.days = diff
    }
  }
})

const formData = ref({
  city: '',
  start_date: '',
  end_date: '',
  days: 3,
  people_count: 2,
  pace: '适中',
  accommodation: '舒适型',
  budget: '',
  preferences: ['自然风景', '美食'] as string[],
  food_preferences: [] as string[],
  extra_requirements: '',
  transportation: '公共交通',
})

const handleSubmit = async () => {
  if (!formData.value.city) {
    message.error('请输入目的地城市')
    return
  }
  if (!startDatePicker.value || !endDatePicker.value) {
    message.error('请选择旅行日期')
    return
  }

  formData.value.start_date = dayjs(startDatePicker.value).format('YYYY-MM-DD')
  formData.value.end_date = dayjs(endDatePicker.value).format('YYYY-MM-DD')

  const start = dayjs(startDatePicker.value)
  const end = dayjs(endDatePicker.value)
  formData.value.days = end.diff(start, 'day') + 1

  if (formData.value.days < 1) {
    message.error('结束日期不能早于开始日期')
    return
  }

  loading.value = true
  loadingProgress.value = 0

  // 获取或生成用户 ID（用于 RAG 偏好记忆）
  let userId = sessionStorage.getItem('trip_user_id')
  if (!userId) {
    userId = 'user_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
    sessionStorage.setItem('trip_user_id', userId)
  }

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += 10
      if (loadingProgress.value <= 25) loadingStatus.value = '🔍 正在搜索景点...'
      else if (loadingProgress.value <= 45) loadingStatus.value = '🌤️ 正在查询天气...'
      else if (loadingProgress.value <= 65) loadingStatus.value = '🏨 正在推荐酒店...'
      else if (loadingProgress.value <= 80) loadingStatus.value = '🧠 正在检索偏好...'
      else loadingStatus.value = '📋 正在生成行程计划...'
    }
  }, 500)

  try {
    const response = await generateTripPlan({
      city: formData.value.city,
      start_date: formData.value.start_date,
      end_date: formData.value.end_date,
      days: formData.value.days,
      preferences: formData.value.preferences.join('、'),
      budget: formData.value.budget || '中等',
      transportation: formData.value.transportation,
      accommodation: formData.value.accommodation,
      food_preferences: formData.value.food_preferences.join('、'),
      extra_requirements: formData.value.extra_requirements,
      user_id: userId,
    })
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingStatus.value = '✅ 完成！正在跳转...'
    sessionStorage.setItem('tripPlan', JSON.stringify(response))
    router.push({ name: 'result' })
  } catch (error) {
    clearInterval(progressInterval)
    message.error('生成计划失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f0f2f5;
}

/* ===== Hero ===== */
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 40%, #24243e 100%);
  padding: 72px 20px 100px;
  text-align: center;
  overflow: hidden;
}

/* 装饰 SVG 动画 */
.deco-plane {
  position: absolute;
  top: 18%;
  right: 12%;
  animation: floatPlane 6s ease-in-out infinite;
  opacity: 0.7;
}
.deco-compass {
  position: absolute;
  bottom: 28%;
  left: 8%;
  animation: floatSlow 8s ease-in-out infinite;
  opacity: 0.6;
}
.deco-pin {
  position: absolute;
  top: 30%;
  left: 15%;
  animation: floatSlow 7s ease-in-out infinite reverse;
  opacity: 0.5;
}
@keyframes floatPlane {
  0%, 100% { transform: translate(0, 0) rotate(-15deg); }
  50% { transform: translate(-20px, -18px) rotate(-10deg); }
}
@keyframes floatSlow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-14px); }
}

.hero-content {
  position: relative;
  z-index: 2;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  color: rgba(255,255,255,0.85);
  padding: 8px 24px;
  border-radius: 24px;
  font-size: 13px;
  letter-spacing: 1px;
  border: 1px solid rgba(255,255,255,0.15);
  margin-bottom: 20px;
}
.hero-title {
  font-size: 48px;
  color: #fff;
  margin: 0 0 16px;
  font-weight: 800;
  letter-spacing: 2px;
}
.hero-subtitle {
  font-size: 16px;
  color: rgba(255,255,255,0.7);
  line-height: 1.8;
  margin: 0;
}
.hero-wave {
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  line-height: 0;
}
.hero-wave svg {
  width: 100%;
  height: 80px;
}

/* ===== 特色卡片 ===== */
.features-row {
  display: flex;
  gap: 16px;
  max-width: 960px;
  margin: -36px auto 32px;
  padding: 0 20px;
  position: relative;
  z-index: 3;
}
.feature-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border-radius: 14px;
  padding: 18px 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  transition: transform 0.25s, box-shadow 0.25s;
}
.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 28px rgba(0,0,0,0.1);
}
.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}
.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}
.feature-desc {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

/* ===== 表单 ===== */
.form-wrapper {
  max-width: 960px;
  margin: 0 auto 40px;
  padding: 0 20px;
}
.form-section {
  background: #fff;
  border-radius: 16px;
  padding: 28px 28px 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.05);
  border: 1px solid rgba(0,0,0,0.04);
}
.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}
.section-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.section-title {
  font-size: 17px;
  font-weight: 700;
  color: #1a1a2e;
}
.section-hint {
  font-size: 13px;
  color: #999;
  margin-top: 2px;
}
.field-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  margin-bottom: 8px;
}
.days-badge {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  text-align: center;
  padding: 8px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 700;
  line-height: 32px;
}

/* 偏好标签 */
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 24px;
  border: 1.5px solid #e8e8e8;
  background: #fafafa;
  font-size: 14px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}
.tag-item:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f0f0ff;
}
.tag-item.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  box-shadow: 0 2px 8px rgba(102,126,234,0.3);
}
.tag-icon {
  font-size: 16px;
}

/* ===== 提交 ===== */
.submit-section {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 20px 20px;
}
.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  height: 54px !important;
  font-size: 17px !important;
  font-weight: 600 !important;
  border-radius: 14px !important;
  display: flex !important;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 24px rgba(102,126,234,0.35);
  transition: all 0.3s;
}
.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(102,126,234,0.45) !important;
}
.loading-section {
  margin-top: 20px;
}
.loading-status {
  text-align: center;
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

/* ===== Footer ===== */
.page-footer {
  text-align: center;
  padding: 24px 20px 32px;
  color: #bbb;
  font-size: 13px;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .hero-title { font-size: 32px; }
  .features-row { flex-direction: column; }
  .deco-plane, .deco-compass, .deco-pin { display: none; }
}
</style>
