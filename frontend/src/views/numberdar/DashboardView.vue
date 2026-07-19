<template>
  <div>
    <DashboardHero
      eyebrow="Numberdar Portal"
      :title="`السلام علیکم، ${firstName}`"
      :subtitle="auth.user?.district ? `${auth.user.district} Community Region` : 'Community Verification Portal'"
      :stats="heroStats"
    />

    <div class="content-container -mt-8 relative z-20">
      <QuickActionsBar :actions="quickActions" />
    </div>

    <DashboardSection id="queue-section" tone="white" eyebrow="Community" title="Farmer Verification Queue">
      <div class="max-w-xl">
        <div :class="['p-4 rounded-xl shadow-sm bg-white border mb-6', community.pendingQueueCount > 0 ? 'border-amber-400' : 'border-gray-100']">
          <p class="text-xs font-medium text-gray-500 mb-1">Pending Approvals</p>
          <p class="text-3xl font-bold" :class="community.pendingQueueCount > 0 ? 'text-amber-600' : 'text-gray-800'">{{ community.pendingQueueCount }}</p>
        </div>
        <router-link to="/numberdar/queue" class="btn-primary inline-flex items-center gap-2">
          Go to Verification Queue →
        </router-link>
      </div>
    </DashboardSection>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { Users, ClipboardCheck, ArrowRight } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth.js'
import { useCommunityStore } from '@/stores/community.js'
import { useScrollTo } from '@/composables/useScrollTo.js'
import DashboardHero from '@/components/layout/DashboardHero.vue'
import DashboardSection from '@/components/layout/DashboardSection.vue'
import QuickActionsBar from '@/components/shared/QuickActionsBar.vue'

const auth = useAuthStore()
const community = useCommunityStore()
const scrollToSection = useScrollTo()

const firstName = computed(() => auth.user?.full_name || 'Numberdar')

const heroStats = computed(() => [
  { icon: ClipboardCheck, label: 'Pending Approvals', value: community.pendingQueueCount },
  { icon: Users, label: 'District', value: auth.user?.district || 'Assigned Area' }
])

const quickActions = computed(() => [
  { label: 'Verification Queue', icon: ClipboardCheck, onClick: () => scrollToSection('queue-section') },
])

onMounted(() => community.fetchQueue())
</script>