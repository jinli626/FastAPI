<template>
  <div class="page-container">
    <el-card shadow="never">
      <div class="table-toolbar">
        <span class="title">分类管理</span>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增分类</el-button>
      </div>

      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="分类名称" min-width="160" />
        <el-table-column prop="sortOrder" label="排序" width="100" align="center" />
        <el-table-column label="新闻数量" width="110" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.newsCount ?? 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170" align="center">
          <template #default="{ row }">{{ formatDateTime(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Edit" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" :icon="Delete" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="420px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number v-model="form.sortOrder" :min="0" :max="9999" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import {
  getCategoriesApi,
  createCategoryApi,
  updateCategoryApi,
  deleteCategoryApi,
} from '@/api/category'
import { formatDateTime } from '@/utils/format'

const loading = ref(false)
const submitting = ref(false)
const list = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新增分类')
const editingId = ref(null)
const formRef = ref()
const form = reactive({ name: '', sortOrder: 0 })

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
}

const fetchList = async () => {
  loading.value = true
  try {
    list.value = await getCategoriesApi()
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingId.value = null
  dialogTitle.value = '新增分类'
  form.name = ''
  form.sortOrder = 0
  dialogVisible.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑分类'
  form.name = row.name
  form.sortOrder = row.sortOrder
  dialogVisible.value = true
}

const resetForm = () => {
  formRef.value?.clearValidate()
}

const onSubmit = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = { name: form.name, sortOrder: form.sortOrder }
      if (editingId.value) {
        await updateCategoryApi(editingId.value, payload)
        ElMessage.success('修改成功')
      } else {
        await createCategoryApi(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchList()
    } catch (e) {
      /* 拦截器已提示 */
    } finally {
      submitting.value = false
    }
  })
}

const onDelete = (row) => {
  ElMessageBox.confirm(`确定删除分类「${row.name}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await deleteCategoryApi(row.id)
      ElMessage.success('删除成功')
      fetchList()
    })
    .catch(() => {})
}

onMounted(fetchList)
</script>

<style scoped>
.table-toolbar .title {
  font-size: 16px;
  font-weight: 600;
}
.hint {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}
</style>
