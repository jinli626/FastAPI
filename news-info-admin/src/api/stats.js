import request from '@/utils/request'

// 概览统计：新闻总数/各状态数/分类数/总浏览量/今日新增
export const getOverviewApi = () => request.get('/api/admin/stats/overview')

// 分类分布：[{ categoryId, categoryName, count }]
export const getCategoryDistributionApi = () => request.get('/api/admin/stats/category-distribution')

// 热门新闻 Top N：[{ id, title, views }]
export const getHotNewsApi = (limit = 10) =>
  request.get('/api/admin/stats/hot-news', { params: { limit } })
