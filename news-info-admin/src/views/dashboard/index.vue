<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.label" :xs="12" :sm="8" :md="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ backgroundColor: card.color }">
            <el-icon :size="22"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-meta">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>分类新闻分布</template>
          <div ref="pieRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>热门新闻 Top 10（按浏览量）</template>
          <div ref="barRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { getOverviewApi, getCategoryDistributionApi, getHotNewsApi } from '@/api/stats'

const overview = reactive({
  newsTotal: 0,
  publishedTotal: 0,
  draftTotal: 0,
  offlineTotal: 0,
  categoryTotal: 0,
  totalViews: 0,
  todayNew: 0,
})

const cards = computed(() => [
  { label: '新闻总数', value: overview.newsTotal, icon: 'Document', color: '#409eff' },
  { label: '已发布', value: overview.publishedTotal, icon: 'CircleCheck', color: '#67c23a' },
  { label: '草稿', value: overview.draftTotal, icon: 'EditPen', color: '#e6a23c' },
  { label: '总浏览量', value: overview.totalViews, icon: 'View', color: '#909399' },
  { label: '分类数', value: overview.categoryTotal, icon: 'Files', color: '#f56c6c' },
  { label: '今日新增', value: overview.todayNew, icon: 'CirclePlus', color: '#9254de' },
])

const pieRef = ref()
const barRef = ref()
let pieChart = null
let barChart = null

const renderPie = (data) => {
  pieChart = echarts.init(pieRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { type: 'scroll', bottom: 0 },
    series: [
      {
        name: '分类分布',
        type: 'pie',
        radius: ['40%', '65%'],
        avoidLabelOverlap: true,
        label: { show: true, formatter: '{b}\n{c}' },
        data: data.map((d) => ({ name: d.categoryName, value: d.count })),
      },
    ],
  })
}

const renderBar = (data) => {
  barChart = echarts.init(barRef.value)
  const items = [...data].reverse() // 横向柱状从上到下由高到低
  barChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 10, right: 24, top: 16, bottom: 10, containLabel: true },
    xAxis: { type: 'value' },
    yAxis: {
      type: 'category',
      data: items.map((i) => (i.title.length > 12 ? i.title.slice(0, 12) + '…' : i.title)),
    },
    series: [
      { type: 'bar', data: items.map((i) => i.views), itemStyle: { color: '#409eff' }, barMaxWidth: 20 },
    ],
  })
}

const resize = () => {
  pieChart?.resize()
  barChart?.resize()
}

onMounted(async () => {
  try {
    Object.assign(overview, await getOverviewApi())
    renderPie(await getCategoryDistributionApi())
    renderBar(await getHotNewsApi(10))
    window.addEventListener('resize', resize)
  } catch (e) {
    /* 拦截器已提示 */
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  pieChart?.dispose()
  barChart?.dispose()
})
</script>

<style scoped>
.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 12px;
}
.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  color: #fff;
  flex-shrink: 0;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-label {
  margin-top: 2px;
  font-size: 13px;
  color: #909399;
}
.chart-row {
  margin-top: 16px;
}
.chart {
  height: 320px;
}
</style>
