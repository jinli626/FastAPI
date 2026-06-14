<template>
  <div class="page-container">
    <el-card v-loading="loading" shadow="never">
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑新闻' : '发布新闻' }}</span>
          <el-button :icon="Back" @click="goBack">返回列表</el-button>
        </div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入新闻标题" maxlength="255" show-word-limit />
        </el-form-item>

        <el-form-item label="简介" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="请输入新闻简介（列表展示用）"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="分类" prop="categoryId">
              <el-select v-model="form.categoryId" placeholder="请选择分类" style="width: 100%">
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="作者">
              <el-input v-model="form.author" placeholder="作者（选填）" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio-button
                  v-for="s in STATUS_OPTIONS"
                  :key="s.value"
                  :value="s.value"
                >
                  {{ s.label }}
                </el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="封面">
          <ImageUpload v-model="form.image" />
        </el-form-item>

        <el-form-item label="正文" prop="content">
          <RichEditor v-model="form.content" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { getNewsDetailApi, createNewsApi, updateNewsApi } from '@/api/news'
import { getCategoriesApi } from '@/api/category'
import { STATUS_OPTIONS } from '@/utils/format'
import RichEditor from '@/components/RichEditor.vue'
import ImageUpload from '@/components/ImageUpload.vue'

const route = useRoute()
const router = useRouter()

const id = computed(() => route.params.id)
const isEdit = computed(() => !!id.value)

const loading = ref(false)
const submitting = ref(false)
const formRef = ref()
const categories = ref([])

const form = reactive({
  title: '',
  description: '',
  author: '',
  categoryId: null,
  status: 'published',
  image: '',
  content: '',
})

const isEmptyHtml = (html) => !html || html.replace(/<[^>]*>/g, '').trim() === ''

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入简介', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择分类', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  content: [
    {
      validator: (rule, value, callback) =>
        isEmptyHtml(value) ? callback(new Error('请输入正文内容')) : callback(),
      trigger: 'blur',
    },
  ],
}

const fetchCategories = async () => {
  categories.value = await getCategoriesApi()
}

const fetchDetail = async () => {
  loading.value = true
  try {
    const data = await getNewsDetailApi(id.value)
    form.title = data.title
    form.description = data.description
    form.author = data.author || ''
    form.categoryId = data.categoryId
    form.status = data.status
    form.image = data.image || ''
    form.content = data.content || ''
  } finally {
    loading.value = false
  }
}

const onSubmit = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = {
        title: form.title,
        description: form.description,
        content: form.content,
        image: form.image || null,
        author: form.author || null,
        categoryId: form.categoryId,
        status: form.status,
      }
      if (isEdit.value) {
        await updateNewsApi(id.value, payload)
        ElMessage.success('保存成功')
      } else {
        await createNewsApi(payload)
        ElMessage.success('发布成功')
      }
      router.push('/news')
    } catch (e) {
      /* 拦截器已提示 */
    } finally {
      submitting.value = false
    }
  })
}

const goBack = () => router.push('/news')

onMounted(async () => {
  try {
    await fetchCategories()
    if (isEdit.value) await fetchDetail()
  } catch (e) {
    /* 拦截器已提示 */
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
