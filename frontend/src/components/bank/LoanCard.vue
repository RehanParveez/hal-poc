<template>
  <div class="border rounded-lg p-4 bg-white shadow-sm">
    <div class="flex justify-between items-start">
      <div>
        <p class="font-semibold">{{ loan.farmer_name }}</p>
        <p class="text-sm text-gray-500">{{ loan.farmer_phone }} • {{ loan.farmer_district }}</p>
        <p class="text-sm text-gray-500">{{ loan.crop_name }} ({{ loan.crop_season }})</p>
      </div>
      <span class="text-xs px-2 py-1 rounded bg-gray-100 capitalize">{{ loan.status.replace('_', ' ') }}</span>
    </div>

    <div class="mt-3 grid grid-cols-2 gap-2 text-sm">
      <div><span class="text-gray-500">Acres applied:</span> {{ loan.acres_applied_for }}</div>
      <div><span class="text-gray-500">Requested:</span> PKR {{ loan.requested_amount }}</div>
      <div v-if="loan.approved_amount"><span class="text-gray-500">Approved:</span> PKR {{ loan.approved_amount }}</div>
      <div v-if="loan.interest_rate_pct"><span class="text-gray-500">Rate:</span> {{ loan.interest_rate_pct }}%</div>
    </div>

    <div v-if="loan.status === 'submitted'" class="mt-4 border-t pt-3 space-y-2">
      <div class="grid grid-cols-2 gap-2">
        <input v-model="approvedAmount" type="number" placeholder="Approved amount" class="border rounded px-2 py-1 text-sm" />
        <input v-model="interestRate" type="number" placeholder="Interest rate %" class="border rounded px-2 py-1 text-sm" />
      </div>
      <div class="flex gap-2">
        <button @click="handleApprove" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Approve</button>
        <button @click="handleReject" class="bg-red-600 text-white px-3 py-1.5 rounded text-sm">Reject</button>
      </div>
    </div>

    <div v-if="loan.status === 'bank_approved'" class="mt-4 border-t pt-3">
      <button @click="handleDisburse" class="bg-blue-700 text-white px-3 py-1.5 rounded text-sm">Disburse</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useLoansStore } from '@/stores/loans.js'

const props = defineProps({
  loan: { type: Object, required: true },
})

const loansStore = useLoansStore()
const approvedAmount = ref('')
const interestRate = ref('')

async function handleApprove() {
  await loansStore.approveLoan(props.loan.id, approvedAmount.value, interestRate.value)
}

async function handleReject() {
  const reason = window.prompt('Rejection reason:')
  if (reason) {
    await loansStore.rejectLoan(props.loan.id, reason)
  }
}

async function handleDisburse() {
  await loansStore.disburseLoan(props.loan.id)
}
</script>