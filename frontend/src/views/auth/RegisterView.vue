<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <form @submit.prevent="handleSubmit" class="bg-white p-8 rounded-lg shadow-md w-full max-w-md space-y-4">
      
      <div class="text-center mb-2">
        <h1 class="text-2xl font-bold text-gray-900">Create Account</h1>
        <p class="text-sm text-gray-500 mt-1">Join the FasalPay AgroChain Platform</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
        <input v-model="form.full_name" type="text" placeholder="e.g., Muhammad Ali" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
          <input v-model="form.phone" type="text" placeholder="03001234567" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">CNIC Number</label>
          <input v-model="form.cnic" type="text" placeholder="35202-1234567-1" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
        <input v-model="form.password" type="password" placeholder="••••••••" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Platform Role</label>
        <select v-model="form.role" required class="w-full border border-gray-300 rounded px-3 py-2 bg-white focus:ring-2 focus:ring-green-600 focus:outline-none">
          <option value="">Select System Access Level</option>
          <option value="smallholder">Smallholder Farmer</option>
          <option value="tenant">Tenant Farmer</option>
          <option value="landowner">Landowner</option>
          <option value="shopkeeper">Shopkeeper</option>
          <option value="bank">Bank Manager</option>
          <option value="factory">Factory Buyer</option>
          <option value="insurance">Insurance Agent</option>
          <option value="afo">AFO Officer</option>
        </select>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">District</label>
          <input v-model="form.district" type="text" placeholder="e.g., Faisalabad" required class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Province</label>
          <input v-model="form.province" type="text" placeholder="Punjab" class="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-green-600 focus:outline-none" />
        </div>
      </div>

      <p v-if="errorMessage" class="text-red-600 text-sm font-medium bg-red-50 p-2 rounded border border-red-200">{{ errorMessage }}</p>

      <button type="submit" :disabled="isSubmitting" class="w-full bg-green-700 hover:bg-green-800 text-white font-medium py-2.5 rounded transition disabled:opacity-50 mt-2">
        {{ isSubmitting ? 'Creating account...' : 'Register' }}
      </button>
      
      <router-link to="/login" class="block text-center text-sm text-gray-600 hover:text-green-700 transition mt-2">Already have an account? Login</router-link>
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