<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
    <div class="bg-white p-6 rounded-lg w-96">
      <h2 class="text-lg font-bold mb-4">Pay Shopkeeper</h2>

      <select v-model="form.input_category" class="w-full border p-2 mb-2">
        <option value="">Select Category</option>
        <option v-for="cat in escrow.spendableCategories" :key="cat" :value="cat">{{ cat }}</option>
      </select>

      <input v-model="form.shopkeeper_id" type="text" placeholder="Shopkeeper User ID" class="w-full border p-2 mb-2" />

      <input v-model.number="form.amount" type="number" placeholder="Amount (PKR)" class="w-full border p-2 mb-2" />

      <div v-if="currentCap" class="text-sm mb-4">
        Limit: {{ currentCap.remaining }} / {{ currentCap.total_cap }} PKR remaining
      </div>

      <button @click="submit" :disabled="inputs.isSubmitting || !form.input_category" class="bg-green-600 text-white w-full py-2 rounded">
        {{ inputs.isSubmitting ? 'Processing...' : 'Pay Now' }}
      </button>
      <button @click="$emit('close')" class="mt-2 w-full text-gray-500">Cancel</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useInputsStore } from '@/stores/inputs.js'
import { useEscrowStore } from '@/stores/escrow.js'

const props = defineProps(['escrowId'])
const emit = defineEmits(['close', 'success'])
const inputs = useInputsStore()
const escrow = useEscrowStore()

const form = reactive({ input_category: '', amount: 0, shopkeeper_id: '' })

const currentCap = computed(() =>
  escrow.caps.find((c) => c.category === form.input_category)
)

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