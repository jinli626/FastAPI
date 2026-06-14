<template>
  <div class="sidebar">
    <div class="logo">
      <el-icon><Promotion /></el-icon>
      <span v-show="!collapsed" class="logo-text">新闻管理后台</span>
    </div>
    <el-menu
      :default-active="activeMenu"
      :collapse="collapsed"
      :collapse-transition="false"
      router
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409eff"
    >
      <el-menu-item v-for="item in items" :key="item.path" :index="item.path">
        <el-icon><component :is="item.icon" /></el-icon>
        <template #title>{{ item.title }}</template>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

defineProps({
  collapsed: { type: Boolean, default: false },
})

const route = useRoute()
const router = useRouter()

const items = computed(() => {
  const layout = router.options.routes.find((r) => r.path === '/')
  if (!layout?.children) return []
  return layout.children
    .filter((c) => !c.meta?.hidden)
    .map((c) => ({
      path: '/' + c.path,
      title: c.meta?.title,
      icon: c.meta?.icon,
    }))
})

// 子页面（如发布/编辑）高亮所属菜单
const activeMenu = computed(() => route.meta?.activeMenu || route.path)
</script>

<style scoped>
.sidebar {
  height: 100%;
}
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 56px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  background-color: #2b3a4d;
}
.logo-text {
  white-space: nowrap;
}
.el-menu {
  border-right: none;
}
</style>
