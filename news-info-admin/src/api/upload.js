import { baseURL } from '@/config/api'
import { getToken } from '@/utils/auth-token'

// el-upload / wangEditor 直接走自身 XHR，这里提供上传地址与鉴权请求头
export const uploadAction = `${baseURL}/api/admin/upload`

export const uploadHeaders = () => ({
  Authorization: `Bearer ${getToken()}`,
})
