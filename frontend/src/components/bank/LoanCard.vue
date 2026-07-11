<template>
  <div class="border rounded-lg p-4 bg-white shadow-sm">
    <div class="flex justify-between items-start">
      <div>
        <p class="font-semibold">{{ loan.farmer_name }}</p>
        <p class="text-sm text-gray-500">{{ loan.farmer_phone }} • {{ loan.farmer_district }}</p>
        <p class="text-sm text-gray-500">{{ loan.crop_name }} ({{ loan.crop_season }})</p>
      </div>
      <StatusBadge :status="loan.status" />
    </div>

    <div class="mt-3 grid grid-cols-2 gap-2 text-sm">
      <div><span class="text-gray-500">Acres applied:</span> {{ loan.acres_applied_for }}</div>
      <div><span class="text-gray-500">Requested:</span> PKR {{ loan.requested_amount }}</div>
      <div v-if="loan.approved_amount"><span class="text-gray-500">Approved:</span> PKR {{ loan.approved_amount }}</div>
      <div v-if="loan.interest_rate_pct"><span class="text-gray-500">Rate:</span> {{ loan.interest_rate_pct }}%</div>
    </div>

    <div v-if="loan.status === 'submitted'" class="mt-4 border-t pt-3 space-y-2">
      <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Approved Amount (PKR)</label>
            <input v-model="approvedAmount" type="number" placeholder="e.g. 50000" class="w-full border rounded px-2 py-1 text-sm" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Interest Rate (%)</label>
            <input v-model="interestRate" type="number" placeholder="e.g. 12.5" class="w-full border rounded px-2 py-1 text-sm" />
          </div>
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
import StatusBadge from '@/components/shared/StatusBadge.vue'
import { ref } from 'vue'
import { useLoansStore } from '@/stores/loans.js'
import { useNotificationsStore } from '@/stores/notifications.js'

const props = defineProps({
  loan: { type: Object, required: true },
})
const loansStore = useLoansStore()
const notify = useNotificationsStore()
const approvedAmount = ref('')
const interestRate = ref('')

async function handleApprove() {
  if (!approvedAmount.value || Number(approvedAmount.value) <= 0) {
    notify.showError('Enter an approved amount greater than zero.')
    return
  }
  if (!interestRate.value || Number(interestRate.value) <= 0 || Number(interestRate.value) > 50) {
    notify.showError('Enter an interest rate between 0 and 50.')
    return
  }

  try {
  await loansStore.approveLoan(props.loan.id, approvedAmount.value, interestRate.value)

  } catch (error) {
    notify.showError(error.response?.data?.error ?? 'Failed to approve loan.')
  }
}

async function handleReject() {
  const reason = window.prompt('Rejection reason:')
  if (reason) {
    try {
    await loansStore.rejectLoan(props.loan.id, reason)
    } catch (error) {
      notify.showError(error.response?.data?.error ?? 'Failed to reject loan.')
    }
  }
}

async function handleDisburse() {
  try {
  await loansStore.disburseLoan(props.loan.id)
  } catch (error) {
    notify.showError(error.response?.data?.error ?? 'Failed to disburse loan.')
  }
}

</script>