<template>
  <div class="forgot-page">
    <van-nav-bar
      title="找回密码"
      left-arrow
      @click-left="onClickLeft"
      fixed
    />

    <div class="forgot-container">
      <div class="forgot-logo">
        <van-image
          width="80"
          height="80"
          src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
          round
        />
        <h2>找回密码</h2>
      </div>

      <!-- 步骤1：输入手机号/邮箱 + 图形验证码 -->
      <van-form v-if="step === 1" @submit="onSendCode" class="forgot-form">
        <van-cell-group inset>
          <van-field
            v-model="contact"
            name="contact"
            label="手机号/邮箱"
            :placeholder="isEmail ? '请输入邮箱地址' : '请输入手机号'"
            :rules="[{ required: true, message: '请输入手机号或邮箱' }]"
          />
          <van-field
            v-model="captchaCode"
            name="captchaCode"
            center
            label="验证码"
            placeholder="请输入计算结果"
            :rules="[{ required: true, message: '请输入验证码答案' }]"
          >
            <template #button>
              <span class="captcha-expression" @click="refreshCaptcha">{{ captchaExpression }}</span>
            </template>
          </van-field>
        </van-cell-group>

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" size="large" :loading="sending">
            发送验证码
          </van-button>
        </div>
      </van-form>

      <!-- 步骤2：输入验证码 -->
      <van-form v-if="step === 2" @submit="onVerifyCode" class="forgot-form">
        <van-cell-group inset>
          <van-field
            v-model="code"
            name="code"
            label="验证码"
            placeholder="请输入6位验证码"
            maxlength="6"
            type="digit"
            :rules="[{ required: true, message: '请输入验证码' }]"
          />
        </van-cell-group>

        <div class="resend-tip">
          <span v-if="countdown > 0">{{ countdown }}秒后可重新发送</span>
          <span v-else class="resend-link" @click="backToStep1">重新发送验证码</span>
        </div>

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" size="large" :loading="verifying">
            下一步
          </van-button>
        </div>
      </van-form>

      <!-- 步骤3：设置新密码 -->
      <van-form v-if="step === 3" @submit="onResetPassword" class="forgot-form">
        <van-cell-group inset>
          <van-field
            v-model="newPassword"
            type="password"
            name="newPassword"
            label="新密码"
            placeholder="请输入新密码（至少6位）"
            :rules="[{ required: true, message: '请输入新密码' }, { validator: validateLength, message: '密码至少6位' }]"
          />
          <van-field
            v-model="confirmPassword"
            type="password"
            name="confirmPassword"
            label="确认密码"
            placeholder="请再次输入新密码"
            :rules="[
              { required: true, message: '请确认新密码' },
              { validator: validatePassword, message: '两次密码不一致' }
            ]"
          />
        </van-cell-group>

        <div class="submit-btn">
          <van-button round block type="primary" native-type="submit" size="large" :loading="resetting">
            确认重置
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import axios from 'axios'
import { apiConfig } from '../config/api'

const router = useRouter()

// 步骤控制
const step = ref(1)

// 步骤1数据
const contact = ref('')
const captchaCode = ref('')
const captchaId = ref('')
const captchaExpression = ref('')
const sending = ref(false)

// 步骤2数据
const code = ref('')
const countdown = ref(0)
let countdownTimer = null
const verifying = ref(false)

// 步骤3数据
const newPassword = ref('')
const confirmPassword = ref('')
const resetToken = ref('')
const resetting = ref(false)

// 判断输入是否为邮箱
const isEmail = computed(() => {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(contact.value)
})

// 获取图形验证码
const fetchCaptcha = async () => {
  try {
    const res = await axios.get(`${apiConfig.baseURL}/api/user/captcha`)
    if (res.data?.code === 200) {
      captchaId.value = res.data.data.captchaId
      captchaExpression.value = res.data.data.expression
    }
  } catch (e) {
    showToast({ type: 'fail', message: '获取验证码失败' })
  }
}

const refreshCaptcha = () => {
  captchaCode.value = ''
  fetchCaptcha()
}

// 步骤1：发送验证码
const onSendCode = async () => {
  if (!contact.value) {
    showToast({ type: 'fail', message: '请输入手机号或邮箱' })
    return
  }
  if (!captchaCode.value) {
    showToast({ type: 'fail', message: '请输入验证码答案' })
    return
  }

  sending.value = true
  try {
    const res = await axios.post(`${apiConfig.baseURL}/api/user/send-code`, {
      contact: contact.value,
      captchaId: captchaId.value,
      captchaCode: captchaCode.value
    })
    if (res.data?.code === 200) {
      showToast({ type: 'success', message: '验证码已发送' })
      step.value = 2
      startCountdown()
    } else {
      showToast({ type: 'fail', message: res.data?.message || '发送失败' })
    }
  } catch (e) {
    const msg = e.response?.status === 429
      ? '发送过于频繁，请稍后再试'
      : (e.response?.data?.message || '发送失败')
    showToast({ type: 'fail', message: msg })
    refreshCaptcha()
  } finally {
    sending.value = false
  }
}

// 倒计时
const startCountdown = () => {
  countdown.value = 60
  if (countdownTimer) clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

// 步骤2：校验验证码
const onVerifyCode = async () => {
  if (!code.value || code.value.length !== 6) {
    showToast({ type: 'fail', message: '请输入6位验证码' })
    return
  }

  verifying.value = true
  try {
    const res = await axios.post(`${apiConfig.baseURL}/api/user/verify-code`, {
      contact: contact.value,
      code: code.value
    })
    if (res.data?.code === 200) {
      resetToken.value = res.data.data.resetToken
      step.value = 3
    } else {
      showToast({ type: 'fail', message: res.data?.message || '验证码错误' })
    }
  } catch (e) {
    showToast({ type: 'fail', message: e.response?.data?.message || '验证失败' })
  } finally {
    verifying.value = false
  }
}

// 表单校验
const validateLength = () => (newPassword.value || '').length >= 6
const validatePassword = () => newPassword.value === confirmPassword.value

// 步骤3：重置密码
const onResetPassword = async () => {
  if (!newPassword.value || newPassword.value.length < 6) {
    showToast({ type: 'fail', message: '密码至少6位' })
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    showToast({ type: 'fail', message: '两次密码不一致' })
    return
  }

  resetting.value = true
  try {
    const res = await axios.put(`${apiConfig.baseURL}/api/user/reset-password`, {
      resetToken: resetToken.value,
      newPassword: newPassword.value
    })
    if (res.data?.code === 200) {
      showToast({ type: 'success', message: '密码重置成功，请登录' })
      setTimeout(() => router.push('/login'), 1500)
    } else {
      showToast({ type: 'fail', message: res.data?.message || '重置失败' })
    }
  } catch (e) {
    showToast({ type: 'fail', message: e.response?.data?.message || '重置失败，请重新验证' })
  } finally {
    resetting.value = false
  }
}

const backToStep1 = () => {
  step.value = 1
  code.value = ''
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 0
  refreshCaptcha()
}

const onClickLeft = () => {
  if (countdownTimer) clearInterval(countdownTimer)
  router.back()
}

// 初始化：获取图形验证码
fetchCaptcha()
</script>

<style scoped>
.forgot-page {
  min-height: 100vh;
  background-color: #f7f8fa;
}

.forgot-container {
  padding-top: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.forgot-logo {
  margin: 40px 0;
  text-align: center;
}

.forgot-logo h2 {
  margin-top: 16px;
  color: #323233;
  font-size: 22px;
}

.forgot-form {
  width: 100%;
  padding: 0 16px;
}

.captcha-expression {
  display: inline-block;
  padding: 4px 12px;
  background: #1989fa;
  color: #fff;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 1px;
  cursor: pointer;
  user-select: none;
}

.submit-btn {
  margin: 24px 16px;
}

.resend-tip {
  text-align: center;
  color: #969799;
  font-size: 14px;
  margin: 12px 16px 0;
}

.resend-link {
  color: #1989fa;
  cursor: pointer;
}
</style>
