<template>
  <div class="image-upload">
    <el-upload
      class="cover-uploader"
      :action="uploadAction"
      :headers="headers"
      :show-file-list="false"
      name="file"
      accept="image/jpeg,image/png,image/gif,image/webp"
      :before-upload="beforeUpload"
      :on-success="onSuccess"
      :on-error="onError"
    >
      <img v-if="modelValue" :src="modelValue" class="cover-img" alt="封面" />
      <el-icon v-else class="uploader-icon"><Plus /></el-icon>
    </el-upload>
    <div v-if="modelValue" class="actions">
      <el-button link type="danger" size="small" @click="clear">移除封面</el-button>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { uploadAction, uploadHeaders } from '@/api/upload'

const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const headers = uploadHeaders()

const beforeUpload = (file) => {
  const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  const okType = allowed.includes(file.type)
  const okSize = file.size / 1024 / 1024 < 5
  if (!okType) ElMessage.error('仅支持 jpg / png / gif / webp 格式')
  if (!okSize) ElMessage.error('图片大小不能超过 5MB')
  return okType && okSize
}

const onSuccess = (res) => {
  // el-upload 走自身 XHR，拿到的是后端原始响应 { code, message, data: { url } }
  if (res.code === 200 && res.data?.url) {
    emit('update:modelValue', res.data.url)
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

const onError = () => ElMessage.error('上传失败，请重试')

const clear = () => emit('update:modelValue', '')
</script>

<style scoped>
.cover-uploader :deep(.el-upload) {
  width: 180px;
  height: 120px;
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.25s;
}
.cover-uploader :deep(.el-upload:hover) {
  border-color: var(--el-color-primary);
}
.cover-img {
  width: 180px;
  height: 120px;
  object-fit: cover;
}
.uploader-icon {
  font-size: 28px;
  color: #8c939d;
}
.actions {
  margin-top: 4px;
}
</style>
