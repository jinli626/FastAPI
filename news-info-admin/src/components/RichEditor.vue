<template>
  <div class="rich-editor">
    <Toolbar
      class="editor-toolbar"
      :editor="editorRef"
      :defaultConfig="toolbarConfig"
      mode="default"
    />
    <Editor
      class="editor-content"
      v-model="valueHtml"
      :defaultConfig="editorConfig"
      mode="default"
      @onCreated="handleCreated"
    />
  </div>
</template>

<script setup>
import '@wangeditor/editor/dist/css/style.css'
import { onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { uploadAction, uploadHeaders } from '@/api/upload'

const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const editorRef = shallowRef()
const valueHtml = ref(props.modelValue)

// 外部值变化时同步进编辑器（如编辑回填）
watch(
  () => props.modelValue,
  (val) => {
    if (val !== valueHtml.value) valueHtml.value = val
  },
)
// 编辑器内容变化时回传
watch(valueHtml, (val) => emit('update:modelValue', val))

const toolbarConfig = {}
const editorConfig = {
  placeholder: '请输入新闻正文...',
  MENU_CONF: {
    uploadImage: {
      server: uploadAction,
      fieldName: 'file',
      headers: uploadHeaders(),
      maxFileSize: 5 * 1024 * 1024,
      allowedFileTypes: ['image/*'],
      // 后端返回 { code, message, data: { url } }，自定义插入
      customInsert(res, insertFn) {
        const url = res?.data?.url
        if (url) insertFn(url, '', url)
      },
    },
  },
}

const handleCreated = (editor) => {
  editorRef.value = editor
}

onBeforeUnmount(() => {
  editorRef.value?.destroy()
})
</script>

<style scoped>
.rich-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  z-index: 1;
}
.editor-toolbar {
  border-bottom: 1px solid #dcdfe6;
}
.editor-content {
  height: 400px;
  overflow-y: hidden;
}
</style>
