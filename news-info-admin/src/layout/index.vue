<template>
  <el-container class="layout">
    <el-aside :width="collapsed ? '64px' : '210px'" class="layout-aside">
      <Sidebar :collapsed="collapsed" />
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <Navbar v-model:collapsed="collapsed" />
      </el-header>
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'

const collapsed = ref(false)
</script>

<style scoped>
.layout {
  height: 100vh;
}
.layout-aside {
  background-color: #304156;
  transition: width 0.25s ease;
  overflow: hidden;
}
.layout-header {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 16px;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}
.layout-main {
  padding: 0;
  background-color: #f0f2f5;
  overflow-y: auto;
}
</style>
