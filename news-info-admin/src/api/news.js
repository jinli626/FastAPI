import request from '@/utils/request'

// 新闻列表（分页 + 搜索 + 分类 + 状态），params: { page, pageSize, categoryId, keyword, status }
export const getNewsListApi = (params) => request.get('/api/admin/news/list', { params })

// 新闻详情（含正文）
export const getNewsDetailApi = (id) => request.get('/api/admin/news/detail', { params: { id } })

// 新建新闻
export const createNewsApi = (data) => request.post('/api/admin/news', data)

// 更新新闻
export const updateNewsApi = (id, data) => request.put(`/api/admin/news/${id}`, data)

// 更新状态：draft / published / offline
export const updateNewsStatusApi = (id, status) =>
  request.patch(`/api/admin/news/${id}/status`, { status })

// 删除新闻
export const deleteNewsApi = (id) => request.delete(`/api/admin/news/${id}`)
