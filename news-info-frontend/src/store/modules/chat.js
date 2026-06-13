import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [
      { role: 'assistant', content: '你好！我是AI助手，有什么可以帮助你的吗？' }
    ]
  }),

  actions: {
    addMessage(message) {
      this.messages.push(message)
    },

    updateLastMessage(content) {
      if (this.messages.length > 0) {
        this.messages[this.messages.length - 1].content = content
      }
    },

    clearMessages() {
      this.messages = [
        { role: 'assistant', content: '你好！我是AI助手，有什么可以帮助你的吗？' }
      ]
    }
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'chat-store',
        storage: localStorage
      }
    ]
  }
})
