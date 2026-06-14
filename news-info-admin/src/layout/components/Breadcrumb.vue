<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item v-for="(item, index) in crumbs" :key="index">
      {{ item }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const crumbs = computed(() => {
  const list = ['首页']
  route.matched.forEach((m) => {
    if (m.meta?.title) list.push(m.meta.title)
  })
  return [...new Set(list)]
})
</script>
