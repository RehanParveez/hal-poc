<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <form @submit.prevent="handleSubmit" class="bg-white p-8 rounded-lg shadow-md w-full max-w-sm space-y-4">
      <h1 class="text-2xl font-bold text-center">Hal Login</h1>

      <div>
        <label class="block text-sm font-medium mb-1">Phone</label>
        <input
          v-model="phone"
          type="text"
          required
          class="w-full border rounded px-3 py-2"
          placeholder="03001234567"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">Password</label>
        <input
          v-model="password"
          type="password"
          required
          class="w-full border rounded px-3 py-2"
        />
      </div>

      <p v-if="auth.loginError" class="text-red-600 text-sm">{{ auth.loginError }}</p>

      <button
        type="submit"
        :disabled="auth.isLoading"
        class="w-full bg-green-700 text-white py-2 rounded disabled:opacity-50"
      >
        {{ auth.isLoading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { ROLE_HOME } from '@/constants/roles.js'

const phone = ref('')
const password = ref('')
const auth = useAuthStore()
const router = useRouter()

async function handleSubmit() {
  try {
    const user = await auth.login(phone.value, password.value)
    router.push(ROLE_HOME[user.role] || '/login')
  } catch (err) {
    
  }
}
</script>