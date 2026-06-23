<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">Insurance Claims</h1>

    <div id="claims-section">
      <div v-if="insurance.isLoading" class="text-gray-500">Loading...</div>
      <div v-else class="space-y-3">
        <div v-for="claim in insurance.claims" :key="claim.id" class="bg-white p-4 rounded shadow">
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold">{{ claim.farmer_name }}</p>
              <p class="text-sm text-gray-500">Claim Amount: PKR {{ claim.claim_amount }}</p>
            </div>
            <StatusBadge :status="claim.status" />
          </div>

          <div v-if="claim.status === 'pending'" class="mt-3 border-t pt-3 space-y-2">
            <input v-model.number="reviewForm[claim.id].approved_amount" type="number" placeholder="Approved Amount (if approving)" class="border rounded px-2 py-1 text-sm w-full" />
            <input v-model="reviewForm[claim.id].reviewer_note" type="text" placeholder="Reviewer note (optional)" class="border rounded px-2 py-1 text-sm w-full" />
            <div class="flex gap-2">
              <button @click="handleReview(claim.id, 'approved')" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">Approve</button>
              <button @click="handleReview(claim.id, 'rejected')" class="bg-red-600 text-white px-3 py-1.5 rounded text-sm">Reject</button>
            </div>
          </div>
        </div>
        <p v-if="insurance.claims.length === 0" class="text-gray-500">No claims yet.</p>
      </div>
    </div>

    <div id="policies-section">
      <h2 class="text-2xl font-bold mt-8 mb-4">All Policies</h2>
      <div class="space-y-2">
        <div v-for="p in insurance.policies" :key="p.id" class="bg-white p-3 rounded shadow flex justify-between text-sm">
          <span>{{ p.farmer_name }} — Coverage PKR {{ p.coverage_amount }}</span>
          <StatusBadge :status="p.status" />
        </div>
        <p v-if="insurance.policies.length === 0" class="text-gray-500">No policies yet.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useInsuranceStore } from '@/stores/insurance.js'
import StatusBadge from '@/components/shared/StatusBadge.vue'

const insurance = useInsuranceStore()
const reviewForm = reactive({})

onMounted(async () => {
  await insurance.fetchClaims()
  await insurance.fetchPolicies()
  insurance.claims.forEach((c) => {
    reviewForm[c.id] = { approved_amount: 0, reviewer_note: '' }
  })
})

async function handleReview(claimId, decision) {
  const form = reviewForm[claimId]
  await insurance.reviewClaim(claimId, decision, form.approved_amount, form.reviewer_note)
}
</script>