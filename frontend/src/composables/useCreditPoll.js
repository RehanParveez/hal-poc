import { computed, onMounted, onUnmounted } from 'vue'
import { useCreditStore } from '@/stores/credit.js'

const TERMINAL_STATUSES = ['completed', 'failed', 'manual_review']

export function useCreditPoll(checkId) {
  const credit = useCreditStore()

  onMounted(() => {
    if (checkId && !TERMINAL_STATUSES.includes(credit.activeCheck?.status)) {
      credit.startPolling(checkId)
    }
  })
  onUnmounted(() => credit.stopPolling())

  const status = computed(() => credit.activeCheck?.status ?? null)
  const tier = computed(() => credit.activeCheck?.risk_tier ?? null)
  const isPending = computed(() => status.value === 'pending')
  const isComplete = computed(() => status.value === 'completed')
  const isFailed = computed(() => status.value === 'failed')

  return { status, tier, isPending, isComplete, isFailed }
}