import request from '@/utils/request'

// 管理员登录，返回 { token, adminInfo }
export const loginApi = (data) => request.post('/api/admin/login', data)

// 获取当前管理员信息
export const getAdminInfoApi = () => request.get('/api/admin/info')

// 修改密码 { oldPassword, newPassword }
export const changePasswordApi = (data) => request.put('/api/admin/password', data)
