// 格式化日期时间为 YYYY-MM-DD HH:mm
export function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (Number.isNaN(d.getTime())) return val
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

// 新闻状态 -> 文案 / 标签类型
export const STATUS_OPTIONS = [
  { value: 'draft', label: '草稿', tag: 'info' },
  { value: 'published', label: '已发布', tag: 'success' },
  { value: 'offline', label: '已下架', tag: 'warning' },
]

export function statusLabel(status) {
  return STATUS_OPTIONS.find((s) => s.value === status)?.label || status
}

export function statusTagType(status) {
  return STATUS_OPTIONS.find((s) => s.value === status)?.tag || 'info'
}
