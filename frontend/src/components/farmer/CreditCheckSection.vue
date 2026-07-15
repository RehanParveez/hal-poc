<template>
  <div v-if="loans.pendingCreditCheckLoan" class="mt-6 bg-white p-4 rounded shadow">
    <h2 class="text-lg font-bold mb-1">Credit Check</h2>
    <p class="text-sm text-gray-500 mb-3">
      Your loan (PKR {{ loans.pendingCreditCheckLoan.approved_amount }}) has been approved by the bank.
      A credit check is required before it can be disbursed.
    </p>
    <CreditResultCard v-if="credit.activeCheck" :credit-check="credit.activeCheck" />
    <CreditConsentForm v-else :loan-id="loans.pendingCreditCheckLoan.id" @consent-complete="handleConsentComplete" />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useLoansStore } from '@/stores/loans.js'
import { useCreditStore } from '@/stores/credit.js'
import CreditConsentForm from './CreditConsentForm.vue'
import CreditResultCard from './CreditResultCard.vue'

const loans = useLoansStore()
const credit = useCreditStore()

async function handleConsentComplete() {
  if (loans.pendingCreditCheckLoan) await credit.runCreditCheck(loans.pendingCreditCheckLoan.id)
}

onMounted(async () => {
  await credit.fetchHistory()
  if (loans.pendingCreditCheckLoan) {
    const existing = credit.checks.find((c) => c.loan_application === loans.pendingCreditCheckLoan.id)
    if (existing) {
      credit.activeCheck = existing
      if (existing.status === 'pending') credit.startPolling(existing.id)
    }
  }
})
watch(() => credit.isApproved || credit.isRejected, (done) => {
  if (done) loans.fetchAllMyLoans()   // refresh so credit_check_status reflects the new result
})
onUnmounted(() => credit.stopPolling())
</script>