<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white p-6 rounded-lg w-96">
      <h2 class="text-lg font-bold mb-4">Pay Shopkeeper</h2>
      
      <label class="block text-xs font-medium text-gray-600 mb-1">Input Category</label>
      <select v-model="form.input_category" class="w-full border p-2 mb-2">
        <option value="">Select Category</option>
        <option v-for="cat in escrow.spendableCategories" :key="cat" :value="cat">{{ cat }}</option>
      </select>
      
      <label class="block text-xs font-medium text-gray-600 mb-1">Shopkeeper</label>
      <select v-model="form.shopkeeper_id" class="w-full border p-2 mb-2">
        <option value="">Select Shopkeeper</option>
        <option v-for="s in shopkeepersList" :key="s.id" :value="s.id">{{ s.name }} ({{ s.phone }})</option>
      </select>
      
      <label class="block text-xs font-medium text-gray-600 mb-1">Amount (PKR)</label>
      <input v-model.number="form.amount" type="number" placeholder="Amount (PKR)" class="w-full border p-2 mb-2" />

      <AFOLimitDisplay
        :category="form.input_category"
        :afoState="{ cap: currentCap?.total_cap || 0, alreadySpent: currentCap?.already_spent || 0, remaining: currentCap?.remaining || 0 }"
      />

      <button @click="submit" :disabled="inputs.isSubmitting || !form.input_category" class="bg-green-600 text-white w-full py-2 rounded">
        {{ inputs.isSubmitting ? 'Processing...' : 'Pay Now' }}
      </button>
      <button @click="$emit('close')" class="mt-2 w-full text-gray-500">Cancel</button>
    </div>
  </div>
</template>

<script setup>
import AFOLimitDisplay from '@/components/farmer/AFOLimitDisplay.vue'
import { reactive, computed, ref, onMounted } from 'vue'
import { useInputsStore } from '@/stores/inputs.js'
import { useEscrowStore } from '@/stores/escrow.js'
import { listShopkeepers } from '@/api/accounts.js'

const props = defineProps(['escrowId'])
const emit = defineEmits(['close', 'success'])
const inputs = useInputsStore()
const escrow = useEscrowStore()
const shopkeepersList = ref([])

const form = reactive({ input_category: '', amount: 0, shopkeeper_id: '' })

const currentCap = computed(() =>
  escrow.caps.find((c) => c.category === form.input_category)
)

onMounted(async () => {
  try {
    const res = await listShopkeepers()
    shopkeepersList.value = res.data
  } catch (error) {
    console.error("Failed to fetch shopkeepers:", error)
  }
})

const submit = async () => {
  if (!form.input_category) return
  await inputs.submitPayment({
    escrow_id: props.escrowId,
    shopkeeper_id: form.shopkeeper_id,
    input_category: form.input_category,
    amount: form.amount,
  })
  emit('success')
}
</script>