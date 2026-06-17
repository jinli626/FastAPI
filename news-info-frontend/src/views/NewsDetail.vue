<template>
  <div class="news-detail">
    <van-nav-bar
      title="新闻详情"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
      fixed
    />
    
    <div class="detail-content" v-if="newsStore.newsDetail.id">
      <div class="title-container">
        <h1 class="title">{{ newsStore.newsDetail.title }}</h1>
        <van-button 
          class="favorite-btn" 
          :icon="isFavorite ? 'star' : 'star-o'" 
          :class="{ 'is-favorite': isFavorite }"
          @click="toggleFavorite"
        />
      </div>
      
      <div class="info">
        <span>{{ newsStore.newsDetail.author }}</span>
        <span>{{ newsStore.newsDetail.publishTime }}</span>
        <span>{{ newsStore.newsDetail.views }} 阅读</span>
      </div>
      
      <div class="cover" v-if="newsStore.newsDetail.image">
        <img :src="newsStore.newsDetail.image" :alt="newsStore.newsDetail.title">
      </div>
      
      <div class="content rich-text" v-html="sanitizedContent"></div>
      
      <div class="related-news" v-if="newsStore.newsDetail.relatedNews?.length">
        <h3>相关推荐</h3>
        <div class="related-list">
          <div 
            class="related-item" 
            v-for="item in newsStore.newsDetail.relatedNews" 
            :key="item.id"
            @click="goToRelatedNews(item.id)"
          >
            <div class="related-image">
              <img :src="item.image" :alt="item.title">
            </div>
            <div class="related-title">{{ item.title }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <van-empty v-else description="加载中..." />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNewsStore } from '../store/modules/news'
import { useHistoryStore } from '../store/modules/history'
import { useFavoriteStore } from '../store/modules/favorite'
import { useUserStore } from '../store/user'
import { showToast } from 'vant'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()
const newsStore = useNewsStore()
const historyStore = useHistoryStore()
const favoriteStore = useFavoriteStore()
const userStore = useUserStore()

// 获取路由参数中的新闻ID
const newsId = computed(() => Number(route.params.id))

// 正文是富文本 HTML，用 DOMPurify 净化后再渲染，避免 XSS
const sanitizedContent = computed(() => {
  if (!newsStore.newsDetail.content) return ''
  return DOMPurify.sanitize(newsStore.newsDetail.content)
})

// 返回上一页
const onClickLeft = () => {
  router.back()
}

// 跳转到相关新闻
const goToRelatedNews = (id) => {
  router.push(`/news/detail/${id}`)
}

// 判断当前新闻是否已收藏
const isFavorite = computed(() => {
  return favoriteStore.isFavorite(newsId.value)
})

// 切换收藏状态
const toggleFavorite = async () => {
  // 判断用户是否已登录
  if (!userStore.getLoginStatus) {
    // 未登录则跳转到登录页
    showToast({
      message: '请先登录后再收藏',
      position: 'bottom',
    })
    router.push('/login')
    return
  }
  
  // 已登录则调用API切换收藏状态
  const status = await favoriteStore.toggleFavorite(newsStore.newsDetail)
  
  if (status === true) {
    showToast({
      message: '已添加到收藏',
      position: 'bottom',
    })
  } else if (status === false) {
    showToast({
      message: '已取消收藏',
      position: 'bottom',
    })
  } else {
    // status为null表示操作失败
    showToast({
      message: '操作失败，请稍后重试',
      position: 'bottom',
    })
  }
}

const loadNewsDetail = async (id) => {
  await newsStore.getNewsDetail(id)

  if (newsStore.newsDetail.id) {
    if (userStore.getLoginStatus) {
      try {
        await historyStore.addHistoryApi(newsStore.newsDetail.id)
      } catch (error) {
        console.error('记录浏览历史API失败:', error)
      }
    }
  }

  favoriteStore.loadFavorites()

  if (userStore.getLoginStatus && newsStore.newsDetail.id) {
    const result = await favoriteStore.checkFavoriteStatusApi(newsStore.newsDetail.id)
    if (result.success && !result.isLocal) {
      if (result.isFavorite && !favoriteStore.isFavorite(newsStore.newsDetail.id)) {
        favoriteStore.addFavorite(newsStore.newsDetail)
      } else if (!result.isFavorite && favoriteStore.isFavorite(newsStore.newsDetail.id)) {
        favoriteStore.removeFavorite(newsStore.newsDetail.id)
      }
    }
  }

  window.scrollTo(0, 0)
}

onMounted(() => loadNewsDetail(newsId.value))

watch(newsId, (newId) => {
  if (newId) loadNewsDetail(newId)
})
</script>

<style scoped>
.news-detail {
  padding-top: 46px;
  background-color: #fff;
  min-height: 100vh;
}

.detail-content {
  padding: 16px;
}

.title-container {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}

.title {
  font-size: 22px;
  font-weight: bold;
  line-height: 1.4;
  margin: 0;
  flex: 1;
}

.favorite-btn {
  flex-shrink: 0;
  margin-left: 10px;
  padding: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
}

.favorite-btn.is-favorite {
  color: #ff9500;
}

.info {
  display: flex;
  font-size: 12px;
  color: #999;
  margin-bottom: 16px;
}

.info span {
  margin-right: 12px;
}

.cover {
  margin-bottom: 16px;
}

.cover img {
  width: 100%;
  border-radius: 4px;
}

.content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  word-break: break-word;
}

/* v-html 注入的内容不带 scoped 标记，需用 :deep() 命中 */
.rich-text :deep(p) {
  margin: 0 0 16px;
  text-align: justify;
}

.rich-text :deep(h1),
.rich-text :deep(h2),
.rich-text :deep(h3),
.rich-text :deep(h4) {
  font-weight: bold;
  line-height: 1.4;
  color: #1a1a1a;
  margin: 28px 0 14px;
}

.rich-text :deep(h1) {
  font-size: 24px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ececec;
}

.rich-text :deep(h2) {
  font-size: 20px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.rich-text :deep(h3) {
  font-size: 18px;
}

.rich-text :deep(h4) {
  font-size: 16px;
}

.rich-text :deep(img),
.rich-text :deep(video) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 8px 0;
}

.rich-text :deep(hr) {
  border: none;
  border-top: 1px solid #eaeaea;
  margin: 20px 0;
}

.rich-text :deep(ul),
.rich-text :deep(ol) {
  padding-left: 24px;
  margin: 0 0 16px;
}

.rich-text :deep(li) {
  margin-bottom: 8px;
}

.rich-text :deep(blockquote) {
  margin: 0 0 16px;
  padding: 8px 14px;
  color: #666;
  background: #f7f8fa;
  border-left: 4px solid #dcdee0;
  border-radius: 0 4px 4px 0;
}

.rich-text :deep(a) {
  color: #1989fa;
  text-decoration: none;
  word-break: break-all;
}

.rich-text :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 16px;
}

.rich-text :deep(th),
.rich-text :deep(td) {
  border: 1px solid #ebedf0;
  padding: 6px 10px;
}

.related-news {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 8px solid #f5f5f5;
}

.related-news h3 {
  font-size: 18px;
  margin: 0 0 16px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  display: flex;
  align-items: center;
}

.related-image {
  width: 80px;
  height: 60px;
  margin-right: 12px;
  flex-shrink: 0;
}

.related-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.related-title {
  font-size: 14px;
  line-height: 1.4;
  flex: 1;
}
</style>