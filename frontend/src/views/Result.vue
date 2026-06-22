<template>
  <div class="result-container">
    <!-- 顶部导航栏 -->
    <div class="top-nav" :class="{ scrolled: isScrolled }">
      <div class="nav-inner">
        <div class="nav-brand" @click="router.push('/')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" fill="currentColor"/>
          </svg>
          旅行助手
        </div>
        <div class="nav-links">
          <a
            v-for="sec in navSections"
            :key="sec.id"
            class="nav-link"
            :class="{ active: activeSection === sec.id }"
            @click.prevent="scrollToSection(sec.id)"
          >{{ sec.label }}</a>
        </div>
        <div class="nav-actions">
          <a-dropdown placement="bottomRight">
            <a-button size="small" class="export-btn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="margin-right:6px"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
              导出
            </a-button>
            <template #overlay>
              <a-menu @click="handleExport">
                <a-menu-item key="image">📷 导出为图片</a-menu-item>
                <a-menu-item key="pdf">📄 导出为PDF</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </div>
    </div>

    <!-- 主内容 -->
    <div class="main-content">
      <div id="trip-plan-content">

        <!-- 行程头部 -->
        <div class="plan-hero" id="overview">
          <div class="plan-hero-bg"></div>
          <div class="plan-hero-content">
            <div class="plan-city">{{ tripPlan.city }}</div>
            <div class="plan-date-range">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/></svg>
              {{ tripPlan.start_date }} 至 {{ tripPlan.end_date }}
              <span class="plan-days-badge">{{ tripPlan.days.length }}天行程</span>
            </div>
            <div class="plan-suggestions" v-if="suggestionItems.length">
              <div class="suggestion-item" v-for="(item, index) in suggestionItems" :key="index">
                <span class="suggestion-num">{{ index + 1 }}</span>
                <span>{{ item }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 预算明细 -->
        <div class="section-block" id="budget" v-if="tripPlan.budget">
          <div class="section-title-row">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="#667eea"><path d="M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/></svg>
            <h2>预算明细</h2>
          </div>
          <div class="budget-cards">
            <div class="budget-card" v-for="b in budgetItems" :key="b.label">
              <div class="budget-icon" :style="{ background: b.bg }">{{ b.icon }}</div>
              <div class="budget-label">{{ b.label }}</div>
              <div class="budget-value">¥{{ b.value }}</div>
            </div>
          </div>
          <div class="budget-total">
            <span>预估总费用</span>
            <span class="total-value">¥{{ tripPlan.budget.total }}</span>
          </div>
        </div>

        <!-- 景点地图 -->
        <div class="section-block" id="map">
          <div class="section-title-row">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="#667eea"><path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/></svg>
            <h2>景点地图</h2>
          </div>
          <div class="map-wrapper">
            <div id="amap-container"></div>
          </div>
        </div>

        <!-- 每日行程 -->
        <div class="section-block" id="days">
          <div class="section-title-row">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="#667eea"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/></svg>
            <h2>每日行程</h2>
          </div>

          <div v-for="(day, dayIndex) in tripPlan.days" :key="dayIndex" class="day-card">
            <!-- 日期头部 -->
            <div class="day-header">
              <div class="day-number">DAY {{ dayIndex + 1 }}</div>
              <div class="day-meta">
                <div class="day-date">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/></svg>
                  {{ day.date }}
                </div>
                <div class="day-location" v-if="day.attractions.length">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>
                  {{ day.attractions[0].name }}{{ day.attractions.length > 1 ? ' 等' + day.attractions.length + '个景点' : '' }}
                </div>
              </div>
            </div>

            <!-- 景点列表 -->
            <div class="attractions-list">
              <div v-for="(attraction, attrIndex) in day.attractions" :key="attrIndex" class="attraction-card">
                <div class="attraction-photo">
                  <img
                    :src="attraction.image_url || '/default-attraction.png'"
                    :alt="attraction.name"
                    :key="attraction.name"
                  />
                  <div class="attraction-index">{{ attrIndex + 1 }}</div>
                </div>
                <div class="attraction-info">
                  <h3>{{ attraction.name }}</h3>
                  <div class="attraction-address">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="#999"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>
                    {{ attraction.address }}
                  </div>
                  <div class="attraction-tags">
                    <span class="tag tag-category" v-if="attraction.category">{{ attraction.category }}</span>
                    <span class="tag tag-ticket">门票 ¥{{ attraction.ticket_price }}</span>
                    <span class="tag tag-time">游览 {{ attraction.visit_duration }}分钟</span>
                  </div>
                  <p class="attraction-desc">{{ attraction.description }}</p>
                  <div v-if="editMode" class="edit-actions">
                    <a-button size="small" @click="moveAttraction(dayIndex, attrIndex, 'up')" :disabled="attrIndex === 0">↑ 上移</a-button>
                    <a-button size="small" @click="moveAttraction(dayIndex, attrIndex, 'down')" :disabled="attrIndex === day.attractions.length - 1">↓ 下移</a-button>
                    <a-button size="small" danger @click="deleteAttraction(dayIndex, attrIndex)">删除</a-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 交通信息 -->
            <div class="day-info-grid">
              <div class="info-item">
                <div class="info-icon" style="background: linear-gradient(135deg, #4facfe, #00f2fe);">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="white"><path d="M12 2c-4 0-8 .5-8 4v9.5C4 17.43 5.57 19 7.5 19L6 20.5v.5h12v-.5L16.5 19c1.93 0 3.5-1.57 3.5-3.5V6c0-3.5-4-4-8-4zM7.5 17c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm3.5-6H6V6h5v5zm5.5 6c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6h-5V6h5v5z"/></svg>
                </div>
                <div>
                  <div class="info-label">交通方式</div>
                  <div class="info-value">{{ day.transportation }}</div>
                </div>
              </div>
              <div class="info-item">
                <div class="info-icon" style="background: linear-gradient(135deg, #f093fb, #f5576c);">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="white"><path d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-8v7H3V7H1v10h22v-6c0-2.21-1.79-4-4-4z"/></svg>
                </div>
                <div>
                  <div class="info-label">住宿安排</div>
                  <div class="info-value">{{ day.accommodation }}</div>
                </div>
              </div>
            </div>

            <!-- 餐饮安排 -->
            <div class="meals-section">
              <div class="meals-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="#667eea"><path d="M8.1 13.34l2.83-2.83L3.91 3.5c-1.56 1.56-1.56 4.09 0 5.66l4.19 4.18zm6.78-1.81c1.53.71 3.68.21 5.27-1.38 1.91-1.91 2.28-4.65.81-6.12-1.46-1.46-4.2-1.1-6.12.81-1.59 1.59-2.09 3.74-1.38 5.27L3.7 19.87l1.41 1.41L12 14.41l6.88 6.88 1.41-1.41L13.41 13l1.47-1.47z"/></svg>
                餐饮安排
              </div>
              <div class="meals-grid">
                <div v-for="(meal, mealIndex) in day.meals" :key="mealIndex" class="meal-card">
                  <span class="meal-type" :class="meal.type">{{ getMealLabel(meal.type) }}</span>
                  <span class="meal-name">{{ meal.name }}</span>
                  <span class="meal-cost">¥{{ meal.estimated_cost }}</span>
                </div>
              </div>
            </div>

            <!-- 住宿信息 -->
            <div class="hotel-section" v-if="day.hotel">
              <div class="hotel-card">
                <div class="hotel-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="#667eea"><path d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-8v7H3V7H1v10h22v-6c0-2.21-1.79-4-4-4z"/></svg>
                </div>
                <div class="hotel-info">
                  <div class="hotel-name">{{ day.hotel.name }}</div>
                  <div class="hotel-address">{{ day.hotel.address }}</div>
                </div>
                <div class="hotel-price">
                  <div class="price-amount">¥{{ day.hotel.estimated_cost }}</div>
                  <div class="price-label">/晚</div>
                </div>
              </div>
            </div>

            <!-- 备注 -->
            <div class="day-notes" v-if="day.description">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="#999"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
              {{ day.description }}
            </div>
          </div>
        </div>

        <!-- 天气信息 -->
        <div class="section-block" id="weather" v-if="tripPlan.weather_info.length">
          <div class="section-title-row">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="#667eea"><path d="M6.76 4.84l-1.8-1.79-1.41 1.41 1.79 1.79 1.42-1.41zM4 10.5H1v2h3v-2zm9-9.95h-2V3.5h2V.55zm7.45 3.91l-1.41-1.41-1.79 1.79 1.41 1.41 1.79-1.79zm-3.21 13.7l1.79 1.8 1.41-1.41-1.8-1.79-1.4 1.4zM20 10.5v2h3v-2h-3zm-8-5c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm-1 16.95h2V19.5h-2v2.95zm-7.45-3.91l1.41 1.41 1.79-1.8-1.41-1.41-1.79 1.8z"/></svg>
            <h2>天气信息</h2>
          </div>
          <div class="weather-grid">
            <div v-for="(weather, index) in tripPlan.weather_info" :key="index" class="weather-card">
              <div class="weather-date">{{ weather.date }}</div>
              <div class="weather-main">
                <div class="weather-day">
                  <span class="weather-label">白天</span>
                  <span class="weather-emoji">{{ getWeatherEmoji(weather.day_weather) }}</span>
                  <span class="weather-temp">{{ weather.day_temp }}°C</span>
                  <span class="weather-desc">{{ weather.day_weather }}</span>
                </div>
                <div class="weather-divider"></div>
                <div class="weather-night">
                  <span class="weather-label">夜间</span>
                  <span class="weather-emoji">{{ getWeatherEmoji(weather.night_weather) }}</span>
                  <span class="weather-temp">{{ weather.night_temp }}°C</span>
                  <span class="weather-desc">{{ weather.night_weather }}</span>
                </div>
              </div>
              <div class="weather-wind">
                {{ weather.wind_direction }} {{ weather.wind_power }}
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>

    <!-- 底部固定操作栏 -->
    <div class="action-bar" :class="{ 'edit-active': editMode }">
      <div class="action-bar-inner">
        <a-button @click="toggleEditMode" :type="editMode ? 'primary' : 'default'" class="action-btn">
          {{ editMode ? '退出编辑' : '✏️ 编辑行程' }}
        </a-button>
        <a-button v-if="editMode" @click="saveChanges" type="primary" class="action-btn save-btn">保存修改</a-button>
        <a-button v-if="editMode" @click="cancelEdit" class="action-btn">取消</a-button>
        <a-button @click="router.push('/')" class="action-btn">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="margin-right:4px"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
          返回首页
        </a-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import type { TripPlan } from '@/types'

const router = useRouter()
const savedPlan = sessionStorage.getItem('tripPlan')
const tripPlan = ref<TripPlan>(savedPlan ? JSON.parse(savedPlan) : {
  city: '',
  start_date: '',
  end_date: '',
  days: [],
  weather_info: [],
  overall_suggestions: ''
})

console.log('Result页面数据:', tripPlan.value)

const navSections = [
  { id: 'overview', label: '行程概览' },
  { id: 'budget', label: '预算明细' },
  { id: 'map', label: '景点地图' },
  { id: 'days', label: '每日行程' },
  { id: 'weather', label: '天气信息' },
]

const suggestionItems = computed(() => {
  if (!tripPlan.value.overall_suggestions) return []
  const text = tripPlan.value.overall_suggestions
  let items = text.split(/(?=\d+[\.\、])/).filter(item => item.trim())
  if (items.length <= 1) {
    items = text.split(/[。；;]/).filter(item => item.trim())
  }
  items = items.map(item => item.replace(/^\d+[\.\、]\s*/, ''))
  return items.length > 0 ? items : [text]
})

const budgetItems = computed(() => {
  if (!tripPlan.value.budget) return []
  const b = tripPlan.value.budget
  return [
    { icon: '🎫', label: '景点门票', value: b.total_attractions, bg: 'linear-gradient(135deg, #667eea22, #764ba222)' },
    { icon: '🏨', label: '酒店住宿', value: b.total_hotels, bg: 'linear-gradient(135deg, #f093fb22, #f5576c22)' },
    { icon: '🍜', label: '餐饮费用', value: b.total_meals, bg: 'linear-gradient(135deg, #43e97b22, #38f9d722)' },
    { icon: '🚌', label: '交通费用', value: b.total_transportation, bg: 'linear-gradient(135deg, #4facfe22, #00f2fe22)' },
  ]
})

const activeSection = ref('overview')
const editMode = ref(false)
const originalPlan = ref<TripPlan | null>(null)
const isScrolled = ref(false)
let map: any = null

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  nextTick(() => { initMap() })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const scrollToSection = (id: string) => {
  activeSection.value = id
  const el = document.getElementById(id)
  if (el) {
    const offset = 70
    const top = el.getBoundingClientRect().top + window.scrollY - offset
    window.scrollTo({ top, behavior: 'smooth' })
  }
}

const getMealLabel = (type: string) => {
  const map: Record<string, string> = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '小食' }
  return map[type] || type
}

const getWeatherEmoji = (weather: string) => {
  if (!weather) return '🌤️'
  if (weather.includes('晴')) return '☀️'
  if (weather.includes('多云')) return '⛅'
  if (weather.includes('阴')) return '☁️'
  if (weather.includes('雨')) return '🌧️'
  if (weather.includes('雪')) return '❄️'
  if (weather.includes('雾') || weather.includes('霾')) return '🌫️'
  return '🌤️'
}

const initMap = async () => {
  if (!tripPlan.value.days.length) return
  try {
    const AMapLoader = (await import('@amap/amap-jsapi-loader')).default
    const AMap = await AMapLoader.load({
      key: 'b906719395017e9e61270bcbe171e381',
      version: '2.0'
    })
    map = new AMap.Map('amap-container', {
      zoom: 12,
      center: [116.397128, 39.916527]
    })
    const markers: any[] = []
    let markerIndex = 1
    tripPlan.value.days.forEach((day) => {
      day.attractions.forEach((attraction) => {
        const marker = new AMap.Marker({
          position: [attraction.location.longitude, attraction.location.latitude],
          title: attraction.name,
          label: { content: `${markerIndex}`, direction: 'top' }
        })
        map.add(marker)
        markers.push(marker)
        markerIndex++
      })
    })
    if (markers.length > 0) {
      map.setFitView(markers)
    }
  } catch (error) {
    console.error('地图加载失败:', error)
  }
}

const toggleEditMode = () => {
  if (editMode.value) {
    if (originalPlan.value) {
      tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
    }
    editMode.value = false
  } else {
    editMode.value = true
    originalPlan.value = JSON.parse(JSON.stringify(tripPlan.value))
  }
}

const moveAttraction = (dayIndex: number, attractionIndex: number, direction: 'up' | 'down') => {
  const attractions = tripPlan.value.days[dayIndex].attractions
  const newIndex = direction === 'up' ? attractionIndex - 1 : attractionIndex + 1
  if (newIndex >= 0 && newIndex < attractions.length) {
    [attractions[attractionIndex], attractions[newIndex]] = [attractions[newIndex], attractions[attractionIndex]]
  }
}

const deleteAttraction = (dayIndex: number, attractionIndex: number) => {
  tripPlan.value.days[dayIndex].attractions.splice(attractionIndex, 1)
}

const saveChanges = () => {
  editMode.value = false
  message.success('修改已保存')
  initMap()
}

const cancelEdit = () => {
  if (originalPlan.value) {
    tripPlan.value = originalPlan.value
  }
  editMode.value = false
}

const handleExport = ({ key }: { key: string }) => {
  if (key === 'image') exportAsImage()
  else if (key === 'pdf') exportAsPDF()
}

const _prepareForExport = () => {
  // 临时隐藏固定元素，避免遮挡内容
  const actionBar = document.querySelector('.action-bar') as HTMLElement
  const topNav = document.querySelector('.top-nav') as HTMLElement
  if (actionBar) actionBar.style.display = 'none'
  if (topNav) topNav.style.display = 'none'
  // 去掉主内容的顶部 padding（导航栏占位）
  const mainContent = document.querySelector('.main-content') as HTMLElement
  const origPadding = mainContent?.style.padding
  if (mainContent) mainContent.style.paddingTop = '0'
  return { actionBar, topNav, mainContent, origPadding }
}

const _restoreAfterExport = (ctx: ReturnType<typeof _prepareForExport>) => {
  if (ctx.actionBar) ctx.actionBar.style.display = ''
  if (ctx.topNav) ctx.topNav.style.display = ''
  if (ctx.mainContent) ctx.mainContent.style.paddingTop = ''
}

const exportAsImage = async () => {
  const element = document.getElementById('trip-plan-content')
  if (!element) return
  const ctx = _prepareForExport()
  try {
    const html2canvas = (await import('html2canvas')).default
    const canvas = await html2canvas(element, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      scrollY: -window.scrollY,
      windowWidth: element.scrollWidth,
      windowHeight: element.scrollHeight,
    })
    const link = document.createElement('a')
    link.download = `${tripPlan.value.city}旅行计划.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    message.success('导出成功！')
  } catch (error) {
    message.error('导出失败')
  } finally {
    _restoreAfterExport(ctx)
  }
}

const exportAsPDF = async () => {
  const element = document.getElementById('trip-plan-content')
  if (!element) return
  const ctx = _prepareForExport()
  try {
    const html2canvas = (await import('html2canvas')).default
    const jsPDF = (await import('jspdf')).default
    const canvas = await html2canvas(element, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      scrollY: -window.scrollY,
      windowWidth: element.scrollWidth,
      windowHeight: element.scrollHeight,
    })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = 210
    const pageHeight = 297
    const margin = 10
    const contentWidth = pageWidth - margin * 2
    const imgHeight = (canvas.height * contentWidth) / canvas.width

    // 如果内容超过一页，分页
    let y = margin
    let remainingHeight = imgHeight
    while (remainingHeight > 0) {
      const sliceHeight = Math.min(remainingHeight, pageHeight - margin * 2)
      pdf.addImage(imgData, 'PNG', margin, y, contentWidth, imgHeight)
      remainingHeight -= (pageHeight - margin * 2)
      if (remainingHeight > 0) {
        pdf.addPage()
        y = -((imgHeight - remainingHeight) * canvas.width / contentWidth) * (contentWidth / canvas.width)
      }
    }
    pdf.save(`${tripPlan.value.city}旅行计划.pdf`)
    message.success('导出成功！')
  } catch (error) {
    message.error('导出失败')
  } finally {
    _restoreAfterExport(ctx)
  }
}
</script>

<style scoped>
.result-container {
  min-height: 100vh;
  background: #f0f2f5;
}

/* ===== Top Nav ===== */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid transparent;
  transition: all 0.3s;
}
.top-nav.scrolled {
  background: rgba(255,255,255,0.95);
  border-bottom-color: #e8e8e8;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 24px;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 15px;
  color: #667eea;
  cursor: pointer;
  margin-right: 32px;
}
.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}
.nav-link {
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}
.nav-link:hover {
  color: #667eea;
  background: #667eea0a;
}
.nav-link.active {
  color: #667eea;
  background: #667eea14;
  font-weight: 600;
}
.nav-actions {
  margin-left: auto;
}
.export-btn {
  border-radius: 8px !important;
  display: flex;
  align-items: center;
}

/* ===== Main Content ===== */
.main-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 72px 24px 80px;
}

/* ===== Plan Hero ===== */
.plan-hero {
  position: relative;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 40%, #24243e 100%);
  border-radius: 20px;
  padding: 48px 40px;
  margin-bottom: 24px;
  overflow: hidden;
}
.plan-hero-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(102,126,234,0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 30%, rgba(118,75,162,0.15) 0%, transparent 50%);
}
.plan-hero-content {
  position: relative;
  z-index: 2;
}
.plan-city {
  font-size: 42px;
  font-weight: 800;
  color: #fff;
  margin-bottom: 12px;
  letter-spacing: 2px;
}
.plan-date-range {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: rgba(255,255,255,0.7);
  margin-bottom: 28px;
}
.plan-days-badge {
  background: rgba(255,255,255,0.15);
  padding: 4px 14px;
  border-radius: 16px;
  font-size: 13px;
  color: rgba(255,255,255,0.9);
  margin-left: 8px;
}
.plan-suggestions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 600px;
}
.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: rgba(255,255,255,0.8);
  font-size: 14px;
  line-height: 1.6;
}
.suggestion-num {
  background: rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.9);
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 2px;
}

/* ===== Section Block ===== */
.section-block {
  background: #fff;
  border-radius: 16px;
  padding: 28px 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.04);
}
.section-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}
.section-title-row h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
}

/* ===== Budget ===== */
.budget-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.budget-card {
  text-align: center;
  padding: 20px 12px;
  border-radius: 14px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  transition: transform 0.2s;
}
.budget-card:hover {
  transform: translateY(-2px);
}
.budget-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  margin: 0 auto 10px;
}
.budget-label {
  font-size: 13px;
  color: #888;
  margin-bottom: 6px;
}
.budget-value {
  font-size: 22px;
  font-weight: 700;
  color: #333;
}
.budget-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea08, #764ba208);
  border-radius: 12px;
  border: 1px solid #667eea20;
}
.budget-total span:first-child {
  font-size: 15px;
  color: #666;
  font-weight: 500;
}
.total-value {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ===== Map ===== */
.map-wrapper {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
}
#amap-container {
  width: 100%;
  height: 400px;
}

/* ===== Day Card ===== */
.day-card {
  background: #fafafa;
  border-radius: 16px;
  padding: 0;
  margin-bottom: 24px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
  transition: box-shadow 0.3s;
}
.day-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.day-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 16px 28px;
  display: flex;
  align-items: center;
  gap: 20px;
}
.day-number {
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 2px;
}
.day-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}
.day-date {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255,255,255,0.85);
  font-size: 14px;
}
.day-location {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255,255,255,0.7);
  font-size: 13px;
  background: rgba(255,255,255,0.15);
  padding: 4px 14px;
  border-radius: 16px;
}

/* Attractions */
.attractions-list {
  padding: 20px 24px 0;
}
.attraction-card {
  display: flex;
  gap: 20px;
  padding: 16px;
  margin-bottom: 12px;
  background: #fff;
  border-radius: 14px;
  border: 1px solid #f0f0f0;
  transition: box-shadow 0.25s, transform 0.25s;
}
.attraction-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  transform: translateY(-1px);
}
.attraction-photo {
  width: 180px;
  height: 130px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}
.attraction-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.attraction-index {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 26px;
  height: 26px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.attraction-info {
  flex: 1;
  min-width: 0;
}
.attraction-info h3 {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 700;
  color: #1a1a2e;
}
.attraction-address {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #999;
  margin-bottom: 10px;
}
.attraction-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}
.tag {
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.tag-category {
  background: #e6f7ff;
  color: #1890ff;
}
.tag-ticket {
  background: #fff7e6;
  color: #fa8c16;
}
.tag-time {
  background: #f6ffed;
  color: #52c41a;
}
.attraction-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.7;
  margin: 0;
}
.edit-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

/* Day Info Grid */
.day-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 24px;
  margin-top: 16px;
}
.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}
.info-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.info-label {
  font-size: 12px;
  color: #999;
}
.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

/* Meals */
.meals-section {
  padding: 0 24px;
  margin-top: 16px;
}
.meals-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #444;
  margin-bottom: 12px;
}
.meals-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.meal-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  font-size: 14px;
}
.meal-type {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 8px;
  font-weight: 500;
}
.meal-type.breakfast { background: #fff7e6; color: #fa8c16; }
.meal-type.lunch { background: #f6ffed; color: #52c41a; }
.meal-type.dinner { background: #e6f7ff; color: #1890ff; }
.meal-type.snack { background: #f9f0ff; color: #722ed1; }
.meal-name {
  font-weight: 500;
  color: #333;
}
.meal-cost {
  color: #999;
  font-size: 13px;
}

/* Hotel */
.hotel-section {
  padding: 0 24px;
  margin-top: 16px;
}
.hotel-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea08, #764ba208);
  border-radius: 14px;
  border: 1px solid #667eea20;
}
.hotel-icon {
  width: 44px;
  height: 44px;
  background: #fff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.hotel-info {
  flex: 1;
}
.hotel-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}
.hotel-address {
  font-size: 13px;
  color: #999;
  margin-top: 2px;
}
.hotel-price {
  text-align: right;
}
.price-amount {
  font-size: 22px;
  font-weight: 800;
  color: #667eea;
}
.price-label {
  font-size: 12px;
  color: #999;
}

/* Notes */
.day-notes {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 16px 24px 20px;
  padding: 14px 16px;
  background: #fffbeb;
  border-radius: 10px;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  border: 1px solid #fde68a40;
}

/* ===== Weather ===== */
.weather-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.weather-card {
  padding: 20px;
  background: #fafafa;
  border-radius: 14px;
  border: 1px solid #f0f0f0;
  text-align: center;
  transition: transform 0.2s;
}
.weather-card:hover {
  transform: translateY(-2px);
}
.weather-date {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 14px;
}
.weather-main {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
}
.weather-day, .weather-night {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.weather-label {
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
}
.weather-emoji {
  font-size: 28px;
}
.weather-temp {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}
.weather-desc {
  font-size: 12px;
  color: #888;
}
.weather-divider {
  width: 1px;
  height: 50px;
  background: #e8e8e8;
}
.weather-wind {
  font-size: 12px;
  color: #999;
}

/* ===== Action Bar (fixed bottom) ===== */
.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-top: 1px solid rgba(0,0,0,0.06);
  padding: 12px 24px;
  transition: all 0.3s;
}
.action-bar.edit-active {
  background: rgba(102,126,234,0.06);
  border-top-color: rgba(102,126,234,0.15);
}
.action-bar-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  gap: 12px;
}
.action-btn {
  border-radius: 10px !important;
  display: flex;
  align-items: center;
}
.save-btn {
  font-weight: 600 !important;
  box-shadow: 0 2px 12px rgba(102,126,234,0.3);
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .plan-city { font-size: 28px; }
  .budget-cards { grid-template-columns: repeat(2, 1fr); }
  .day-info-grid { grid-template-columns: 1fr; }
  .attraction-card { flex-direction: column; }
  .attraction-photo { width: 100%; height: 180px; }
  .weather-grid { grid-template-columns: 1fr; }
  .nav-links { display: none; }
}
</style>
