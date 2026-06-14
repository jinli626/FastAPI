import request from '@/utils/request'

// 分类列表（含每个分类的新闻数量 newsCount）
export const getCategoriesApi = () => request.get('/api/admin/categories')

// 新建分类
export const createCategoryApi = (data) => request.post('/api/admin/categories', data)

// 更新分类
export const updateCategoryApi = (id, data) => request.put(`/api/admin/categories/${id}`, data)

// 删除分类（该分类下有新闻时后端会拒绝）
export const deleteCategoryApi = (id) => request.delete(`/api/admin/categories/${id}`)
