<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <form @submit.prevent="handleSubmit" class="bg-white p-8 rounded-lg shadow-md w-full max-w-sm space-y-3">
      <h1 class="text-2xl font-bold text-center mb-2">Create Account</h1>
      <input v-model="form.full_name" type="text" placeholder="Full Name" required class="w-full border rounded px-3 py-2" />
      <input v-model="form.phone" type="text" placeholder="Phone (03001234567)" required class="w-full border rounded px-3 py-2" />
      <input v-model="form.cnic" type="text" placeholder="CNIC (35202-1234567-1)" required class="w-full border rounded px-3 py-2" />
      <input v-model="form.password" type="password" placeholder="Password" required class="w-full border rounded px-3 py-2" />
      <select v-model="form.role" required class="w-full border rounded px-3 py-2">
        <option value="">Select Role</option>
        <option value="smallholder">Smallholder Farmer</option>
        <option value="tenant">Tenant Farmer</option>
        <option value="landowner">Landowner</option>
        <option value="shopkeeper">Shopkeeper</option>
        <option value="bank">Bank Manager</option>
        <option value="factory">Factory Buyer</option>
        <option value="insurance">Insurance Agent</option>
        <option value="afo">AFO Officer</option>
      </select>
      <input v-model="form.district" type="text" placeholder="District" required class="w-full border rounded px-3 py-2" />
      <input v-model="form.province" type="text" placeholder="Province" class="w-full border rounded px-3 py-2" />
      <p v-if="errorMessage" class="text-red-600 text-sm">{{ errorMessage }}</p>
      <button type="submit" :disabled="isSubmitting" class="w-full bg-green-700 text-white py-2 rounded disabled:opacity-50">
        {{ isSubmitting ? 'Creating account...' : 'Register' }}
      </button>
      <router-link to="/login" class="block text-center text-sm text-gray-500 mt-2">Already have an account? Login</router-link>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const router = useRouter()
const auth = useAuthStore()
const isSubmitting = ref(false)
const errorMessage = ref('')

const form = reactive({ full_name: '', phone: '', cnic: '', password: '', role: '', district: '', province: 'Punjab' })

const ROLE_HOME = {
  smallholder: '/farmer/dashboard', tenant: '/farmer/dashboard', landowner: '/landowner/dashboard',
  bank: '/bank/dashboard', factory: '/factory/dashboard', shopkeeper: '/shopkeeper/dashboard',
  insurance: '/insurance/dashboard', afo: '/afo/dashboard',
}

async function handleSubmit() {
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    const user = await auth.register({ ...form })
    router.push(ROLE_HOME[user.role] || '/login')
  } catch (err) {
    errorMessage.value = err.response?.data?.message || Object.values(err.response?.data || {})[0]?.[0] || 'Registration failed.'
  } finally {
    isSubmitting.value = false
  }
}
</script>