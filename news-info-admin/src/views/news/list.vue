<template>
  <div class="page-container">
    <!-- 搜索栏 -->
    <el-card class="search-bar" shadow="never">
      <el-form :inline="true" @submit.prevent>
        <el-form-item label="标题">
          <el-input
            v-model="query.keyword"
            placeholder="按标题搜索"
            clearable
            style="width: 200px"
            @keyup.enter="onSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="query.categoryId" placeholder="全部分类" clearable style="width: 160px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option v-for="s in STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
          <el-button :icon="Refresh" @click="onReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格 -->
    <el-card shadow="never">
      <div class="table-toolbar">
        <span class="title">新闻列表</span>
        <el-button type="primary" :icon="Plus" @click="goCreate">发布新闻</el-button>
      </div>

      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column label="封面" width="100" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="row.image"
              :preview-src-list="[row.image]"
              preview-teleported
              fit="cover"
              style="width: 60px; height: 40px; border-radius: 4px"
            />
            <span v-else class="muted">无</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column label="分类" width="120" align="center">
          <template #default="{ row }">{{ categoryName(row.categoryId) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览量" width="90" align="center" />
        <el-table-column label="发布时间" width="160" align="center">
          <template #default="{ row }">{{ formatDateTime(row.publishTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Edit" @click="goEdit(row.id)">编辑</el-button>
            <el-button
              v-if="row.status !== 'published'"
              link
              type="success"
              @click="changeStatus(row, 'published')"
            >
              发布
            </el-button>
            <el-button v-else link type="warning" @click="changeStatus(row, 'offline')">
              下架
            </el-button>
            <el-button link type="danger" :icon="Delete" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="fetchList"
          @size-change="onSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getNewsListApi, deleteNewsApi, updateNewsStatusApi } from '@/api/news'
import { getCategoriesApi } from '@/api/category'
import { formatDateTime, statusLabel, statusTagType, STATUS_OPTIONS } from '@/utils/format'

const router = useRouter()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const categories = ref([])

const query = reactive({
  page: 1,
  pageSize: 10,
  keyword: '',
  categoryId: null,
  status: '',
})

const categoryName = (id) => categories.value.find((c) => c.id === id)?.name || '-'

const fetchCategories = async () => {
  try {
    categories.value = await getCategoriesApi()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

const fetchList = async () => {
  loading.value = true
  try {
    const params = {
      page: query.page,
      pageSize: query.pageSize,
    }
    if (query.keyword) params.keyword = query.keyword
    if (query.categoryId) params.categoryId = query.categoryId
    if (query.status) params.status = query.status
    const data = await getNewsListApi(params)
    list.value = data.list
    total.value = data.total
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

const onSearch = () => {
  query.page = 1
  fetchList()
}

const onReset = () => {
  query.keyword = ''
  query.categoryId = null
  query.status = ''
  query.page = 1
  fetchList()
}

const onSizeChange = () => {
  query.page = 1
  fetchList()
}

const goCreate = () => router.push('/news/create')
const goEdit = (id) => router.push(`/news/edit/${id}`)

const changeStatus = async (row, status) => {
  try {
    await updateNewsStatusApi(row.id, status)
    ElMessage.success(status === 'published' ? '已发布' : '已下架')
    fetchList()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

const onDelete = (row) => {
  ElMessageBox.confirm(`确定删除新闻「${row.title}」吗？此操作不可恢复。`, '提示', {
    type: 'warning',
  })
    .then(async () => {
      await deleteNewsApi(row.id)
      ElMessage.success('删除成功')
      // 删除后若当前页空了，回退一页
      if (list.value.length === 1 && query.page > 1) query.page -= 1
      fetchList()
    })
    .catch(() => {})
}

onMounted(async () => {
  await fetchCategories()
  fetchList()
})
</script>

<style scoped>
.table-toolbar .title {
  font-size: 16px;
  font-weight: 600;
}
.muted {
  color: #c0c4cc;
}
</style>
