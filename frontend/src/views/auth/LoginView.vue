<template>
  <div class="min-h-screen flex">
    <div class="hidden lg:flex lg:w-[42%] relative flex-col justify-between p-12 bg-slate-950 text-white overflow-hidden login-texture animate-fade-in-up">
      <div class="relative z-10 flex items-center gap-2">
        <Wheat :size="26" class="text-gold-400" />
        <span class="text-2xl font-display font-semibold tracking-tight">Hal</span>
      </div>

      <div class="relative z-10 space-y-4 max-w-sm mt-auto">
        <div class="bg-slate-950/40 backdrop-blur-xs p-4 rounded-xl border border-white/5">
          <p class="text-lg leading-relaxed text-slate-100 font-display">
            Every phase of the loan unlocks with the crop itself — funded step by step, not handed over all at once.
          </p>
        </div>
        <p class="text-xs text-slate-400/80 tracking-wide">Punjab · Pakistan</p>
      </div>
    </div>

    <div class="flex-1 flex items-center justify-center bg-gray-50 px-4">
      <form @submit.prevent="handleSubmit" class="bg-white p-8 rounded-2xl shadow-sm border border-gray-200 w-full max-w-sm space-y-4 animate-fade-in-up">
        <h1 class="text-2xl font-bold text-center">Hal Login</h1>

        <div>
          <label class="block text-sm font-medium mb-1">Phone</label>
          <input v-model="phone" type="text" required class="w-full border border-gray-300 rounded-lg px-3 py-2" placeholder="03001234567" />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input v-model="password" type="password" required class="w-full border border-gray-300 rounded-lg px-3 py-2" />
        </div>

        <p v-if="auth.loginError" class="text-red-600 text-sm">{{ auth.loginError }}</p>

        <button type="submit" :disabled="auth.isLoading"
          class="w-full bg-green-700 hover:bg-green-800 text-white py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50">
          {{ auth.isLoading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Wheat } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth.js'
import { ROLE_HOME } from '@/constants/roles.js'

const router = useRouter()
const auth = useAuthStore()

const phone = ref('')
const password = ref('')

async function handleSubmit() {
  try {
    const user = await auth.login(phone.value, password.value)
    router.push(ROLE_HOME[user.role] ?? '/login')
  } catch {
  }
}
</script>