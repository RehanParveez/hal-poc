<template>
  <DashboardHero
    eyebrow="Factory Portal"
    :title="`${greeting}, ${firstName}`"
    subtitle="Manage harvest deliveries, post procurement contracts, and settle bank invoices."
    :stats="heroStats"
  />

  <div class="content-container -mt-8 relative z-20">
    <QuickActionsBar :actions="quickActions" />
  </div>

  <DashboardSection v-if="!auth.isCorporateVerified" tone="white" eyebrow="Action Required" title="Account Pending">
    <div class="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-xl text-sm font-medium">
      ⚠ Your business registration (SECP/NTN) is pending admin verification. You cannot post new contracts until this is confirmed.
    </div>
  </DashboardSection>

  <DashboardSection id="deliveries-section" tone="tint" eyebrow="Logistics" title="Deliveries & Grading">
    <div v-if="delivery.isLoading" class="text-gray-500">Loading...</div>
    <div v-else class="space-y-3">
      <div v-for="batch in delivery.batches" :key="batch.id" class="bg-white p-4 rounded shadow">
        <div class="flex justify-between items-start">
          <div>
            <p class="font-semibold">Batch #{{ batch.id.slice(0, 8) }}</p>
            <p class="text-sm text-gray-500">{{ batch.batch_kg }} kg — Expected: PKR {{ batch.expected_payout }}</p>
          </div>
          <StatusBadge :status="batch.status" />
        </div>

        <div v-if="batch.status === 'in_transit'" class="mt-3">
          <button @click="handleMarkReceived(batch.id)" class="bg-blue-700 text-white px-3 py-1.5 rounded text-sm">
            Mark Received
          </button>
        </div>

        <div v-if="batch.status === 'received' && gradeForm[batch.id]" class="mt-3 border-t pt-3 space-y-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Quality Grade</label>
          <select v-model="gradeForm[batch.id].grade_received" class="border rounded px-2 py-1 text-sm w-full">
            <option value="">Select Grade</option>
            <option value="Grade A">Grade A</option>
            <option value="Grade B">Grade B</option>
            <option value="Grade C">Grade C</option>
          </select>
          <label class="block text-xs font-medium text-gray-600 mb-1">Deduction Percentage</label>
          <input v-model.number="gradeForm[batch.id].grade_deduction_pct" type="number" placeholder="Deduction %" class="border rounded px-2 py-1 text-sm w-full" />
          <button @click="submitGrade(batch.id)" class="bg-green-700 text-white px-3 py-1.5 rounded text-sm">
            Confirm Grade
          </button>
        </div>
      </div>
      <p v-if="delivery.batches.length === 0" class="text-gray-500">No deliveries yet.</p>
    </div>
    </DashboardSection>

  <DashboardSection id="settlements-section" tone="white" eyebrow="Finance" title="Bank Settlements">
    <div v-for="inv in settlements.invoices.filter(i => i.status === 'advanced')" :key="inv.id" class="bg-white p-4 rounded shadow mb-3 flex justify-between items-center">
      <span class="text-sm">Invoice #{{ inv.id.slice(0, 8) }} — PKR {{ inv.gross_payout }}</span>
      <button @click="handleFactorySettle(inv.id)" class="bg-purple-700 text-white px-3 py-1.5 rounded text-sm">Settle with Bank</button>
    </div>
   </DashboardSection>

  <DashboardSection id="post-contract-section" tone="tint" eyebrow="Procurement" title="Post New Contract">
    <PostContractForm />
  </DashboardSection>
</template>

<script setup>
import { onMounted, reactive, watch, computed } from 'vue'
import { useDeliveryStore } from '@/stores/delivery.js'
import { useSettlementsStore } from '@/stores/settlements.js'
import { useNotificationsStore } from '@/stores/notifications.js'
import PostContractForm from '@/components/factory/PostContractForm.vue'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import { useAuthStore } from '@/stores/auth.js'
import { Truck, FileSignature, Banknote, Building2 } from 'lucide-vue-next'
import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import QuickActionsBar from '@/components/shared/QuickActionsBar.vue'
import { useScrollTo } from '@/composables/useScrollTo.js'

const delivery = useDeliveryStore()
const settlements = useSettlementsStore()
const notify = useNotificationsStore()
const gradeForm = reactive({})
const auth = useAuthStore() 
const scrollToSection = useScrollTo()

const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || 'Factory')
const greeting = computed(() => {
  const hour = new Date().getHours()
  return hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
})

const heroStats = computed(() => [
  { icon: Truck, label: 'Pending Deliveries', value: delivery.batches.filter(b => b.status === 'in_transit').length },
  { icon: Building2, label: 'Verified Status', value: auth.isCorporateVerified ? 'Verified' : 'Pending' },
  { icon: Banknote, label: 'Open Invoices', value: settlements.invoices.filter(i => i.status === 'advanced').length },
])

const quickActions = computed(() => [
  { label: 'Receive Delivery', icon: Truck, onClick: () => scrollToSection('deliveries-section') },
  { label: 'Bank Settlements', icon: Banknote, onClick: () => scrollToSection('settlements-section') },
  { label: 'Post Contract', icon: FileSignature, onClick: () => scrollToSection('post-contract-section') },
])

function syncGradeForm() {
  delivery.batches.forEach((b) => {
    if (!gradeForm[b.id]) {
      gradeForm[b.id] = { grade_received: '', grade_deduction_pct: 0 }
    }
  })
}

onMounted(async () => {
  await delivery.fetchBatches()
  syncGradeForm()
  await settlements.fetchInvoices()
})

watch(() => delivery.batches, syncGradeForm)

async function submitGrade(batchId) {
  const form = gradeForm[batchId]
  if (!form.grade_received) {
    notify.showError({ message: 'Select a grade before confirming.' })
    return
  }
  if (form.grade_deduction_pct < 0 || form.grade_deduction_pct > 100) {
    notify.showError({ message: 'Deduction percentage must be between 0 and 100.' })
    return
  }
  try {
    await delivery.confirmGrade(batchId, form.grade_received, form.grade_deduction_pct, '')
  } catch (error) {
    notify.showError(error.response?.data ?? { message: 'Failed to confirm grade.' })
  }
}

async function handleMarkReceived(batchId) {
  try {
    await delivery.markReceived(batchId)
  } catch (error) {
    notify.showError(error.response?.data ?? { message: 'Failed to mark batch received.' })
  }
}

async function handleFactorySettle(invoiceId) {
  try {
    await settlements.factorySettle(invoiceId)
  } catch (error) {
    notify.showError(error.response?.data ?? { message: 'Failed to settle with bank.' })
  }
}

</script>